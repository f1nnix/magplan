import datetime
import io
import os
from zipfile import ZipFile, ZIP_DEFLATED

import html2text
from constance import config
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.mail import EmailMultiAlternatives
from django.http import HttpRequest
from django.shortcuts import render, HttpResponse, redirect
from django.template import Template, Context
from django.template.loader import render_to_string
from slugify import slugify

from main.models import Post, Postype, Stage, Idea, Attachment, Comment, User, users_with_perm
from plan.forms import PostBaseModelForm, PostExtendedModelForm, CommentModelForm, PostMetaForm


# Create your views here.
def _get_arbitrary_chunk(post: Post) -> str:
    """Render instance specific template code

    Used to render some arbitrary HTML code in a context of Post instance.
    Useful to provide sensitive HTML template, which can't be committed
    into Git repository directly or may vary for each particular instance.

    :param post: Post instance to use in template
    :return: Rendered template string
    """
    instance_template = Template(config.PLAN_POSTS_INSTANCE_CHUNK)
    instance_chunk = instance_template.render(Context({
        'post': post,
    }))
    return instance_chunk


@login_required
def show(request, post_id):
    post = Post.objects \
        .prefetch_related('editor', 'authors', 'stage', 'section', 'issues', 'comments__user') \
        .get(id=post_id)

    post_meta_form = PostMetaForm(initial={'wp_id': post.meta.get('wpid', None)},
                                  instance=post)

    return render(request, 'plan/posts/show.html', {
        'post': post,
        'stages': Stage.objects.order_by('sort').all(),
        'instance_chunk': _get_arbitrary_chunk(post),
        'comment_form': CommentModelForm(),
        'meta_form': post_meta_form,

        'TYPE_CHOICES': Comment.TYPE_CHOICES,
        'SYSTEM_ACTION_CHOICES': Comment.SYSTEM_ACTION_CHOICES,
    })


@login_required
def create(request):
    if request.method == 'POST':
        form = PostBaseModelForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            post.editor = request.user
            post.postype = Postype.objects.get(slug='article')
            post.stage = Stage.objects.get(slug='waiting')

            post.save()
            form.save_m2m()

            idea = Idea.objects.get(id=request.POST.get('idea_id', None))
            idea.post = post
            idea.save()

            return redirect('posts_show', post.id)

    else:
        return HttpResponse(status=405)


@login_required
def edit(request, post_id):
    post = (Post.objects
            .prefetch_related('editor', 'authors', 'stage', 'section', 'issues', )
            .get(id=post_id))

    if request.method == 'POST':
        form = PostExtendedModelForm(request.POST, request.FILES, instance=post)
        files = request.FILES.getlist('attachments')

        attachments = []
        for file in files:
            attachment = Attachment(post=post, user=request.user, original_filename=file.name)  # save original filename

            # Slugify original filename and save with safe one
            filename, extension = os.path.splitext(file.name)
            file.name = '%s%s' % (slugify(filename), extension)

            # assign file object with slugified filename as name, original is copied by value
            attachment.file = file

            if file.content_type in ('image/png', 'image/jpeg'):
                attachment.type = Attachment.TYPE_IMAGE
            elif file.content_type == 'application/pdf':
                attachment.type = Attachment.TYPE_PDF
            else:
                attachment.type = Attachment.TYPE_FILE

            attachment.save()
            attachments.append(attachment)

        if form.is_valid():
            post.meta['wpid'] = request.POST.get('wp_id', None)
            post.imprint_updater(request.user)
            form.save()

            messages.add_message(request, messages.SUCCESS, 'Пост «%s» успешно отредактирован' % post)

            # create system comment
            if config.SYSTEM_USER_ID:
                system_user = User.objects.get(id=config.SYSTEM_USER_ID)
                comment = Comment()
                comment.commentable = post
                comment.type = Comment.TYPE_SYSTEM
                comment.user = system_user

                meta = {
                    'action': Comment.SYSTEM_ACTION_UPDATE,
                    'user': {
                        'id': request.user.id,
                        'str': request.user.__str__(),
                    },
                    'files': [],

                }
                if len(attachments) > 0:
                    meta['files'] = [{
                        'id': a.id,
                        'str': a.original_filename
                    } for a in attachments]
                comment.meta['comment'] = meta

                comment.save()

                return redirect('posts_edit', post_id)

        else:
            messages.add_message(request, messages.ERROR, 'При обновлении поста произошла ошибка ввода')


    else:
        form = PostExtendedModelForm(initial={
            'wp_id': post.meta.get('wpid', None)}, instance=post)

    return render(request, 'plan/posts/edit.html', {
        'post': post,
        'form': form,

    })


@login_required
def edit_meta(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return HttpResponse(status=401)

    if request.method == 'POST':
        form = PostMetaForm(request.POST, instance=post)
        if not form.is_valid():
            return HttpResponse(status=403)

        # Iterate over all changeable attributes and stage changes in logs
        changelog = []
        new_issues = form.cleaned_data.get('issues', ())
        if post.issues != new_issues:
            # Stage change
            log = '* выпуски сменились с "{0}" на "{1}"'.format(
                ', '.join([str(i) for i in post.issues.all()]),
                ', '.join([str(i) for i in new_issues])
            )
            changelog.append(log)
            post.issues.set(new_issues)

        if post.editor != form.cleaned_data.get('editor'):
            log = '* редактор вменился с "{0}" на "{1}"'.format(
                str(post.editor),
                str(form.cleaned_data.get('editor'))
            )
            changelog.append(log)
            post.editor = form.cleaned_data.get('editor')

        if request.user.is_member('Managing editors'):
            ...

        post.save()
        messages.add_message(request, messages.INFO, f'Пост {post} успешно обновлен!')

    return redirect('posts_show', post_id)


@login_required
def set_stage(request, post_id, system=Comment.TYPE_SYSTEM):
    post = (Post.objects
            .get(id=post_id))
    if request.method == 'POST' and request.POST.get('new_stage_id', None):
        stage = Stage.objects.get(id=request.POST.get('new_stage_id', None))

        # set deadline to current stage durtion. If no duration, append 1 day
        duration = stage.duration if stage.duration else 1
        post.finished_at = post.finished_at + + datetime.timedelta(days=duration)
        post.stage = stage
        post.imprint_updater(request.user)
        post.save()
        messages.add_message(request, messages.INFO, 'Текущий этап статьи «%s» обновлен' % post)

        # create system comment
        if config.SYSTEM_USER_ID:
            system_user = User.objects.get(id=config.SYSTEM_USER_ID)
            comment = Comment()
            comment.commentable = post
            comment.type = system
            comment.user = system_user

            comment.meta['comment'] = {
                'action': Comment.SYSTEM_ACTION_SET_STAGE,
                'stage': {
                    'id': post.stage.id,
                    'str': post.stage.__str__(),
                },
                'user': {
                    'id': request.user.id,
                    'str': request.user.__str__(),
                },

            }
            comment.save()

        # send email if stage allows it
        if post.assignee != request.user and stage.skip_notification is False:
            subject = f'На вас назначена статья «{post}»'
            html_content = render_to_string('email/assigned_to_you.html', {
                'post': post,
                'APP_URL': os.environ.get('APP_URL', None),
            })
            text_content = html2text.html2text(html_content)
            msg = EmailMultiAlternatives(subject, text_content, config.PLAN_EMAIL_FROM, [post.assignee.email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            return redirect('posts_show', post_id)

    return redirect('posts_show', post.id)


@login_required
@permission_required('main.edit_extended_post_attrs')
def schedule(request, post_id):
    post = Post.objects.get(id=post_id)
    published_at = request.POST.get('published_at')

    if published_at is None:
        messages.add_message(request, messages.ERROR, 'Ошибка планирования публикации — дата не передана')
        return redirect('posts_show', post.id)

    dt = datetime.datetime.strptime(published_at, '%Y-%m-%d')
    dt = dt.replace(hour=10, minute=0, second=0)
    post.published_at = dt
    post.save()

    messages.add_message(request, messages.SUCCESS, 'Пост успешно запланирован в публикацию')

    return redirect('posts_show', post.id)


@login_required
def comments(request, post_id):
    post = Post.objects.prefetch_related('editor', 'authors', 'stage', 'section', 'issues', 'comments__user').get(
        id=post_id)
    
    if request.method == 'POST':
        form = CommentModelForm(request.POST)

        comment = form.save(commit=False)
        comment.commentable = post
        comment.user = request.user

        if form.is_valid():
            form.save()

            # Send notification to users with 'recieve_post_email_updates' permission
            recipients = {
                u.get('email')
                for u in users_with_perm('recieve_post_email_updates')
                    .values('email')
                    .exclude(id=comment.user.id)
            }

            # Add post editor if it's not he's comment
            if post.editor != request.user:
                recipients.add(post.editor.email)

            if len(recipients) == 0:
                return redirect('posts_show', post_id)
                
            subject = f'Комментарий к посту «{post}» от {comment.user}'
            html_content = render_to_string('email/new_comment.html', {
                'comment': comment,
                'commentable_type': 'post' if comment.commentable.__class__.__name__ == 'Post' else 'idea',
                'APP_URL': os.environ.get('APP_URL', None),
            })
            text_content = html2text.html2text(html_content)
            
            msg = EmailMultiAlternatives(subject, text_content, config.PLAN_EMAIL_FROM, recipients)
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            return redirect('posts_show', post_id)

    return render(request, 'plan/posts/show.html', {
        'post': post,
        'stages': Stage.objects.order_by('sort').all(),
        'form': CommentModelForm(),
    })


@login_required
def attachment_delete(request, post_id):
    if request.method == 'POST':
        try:
            attachemnt = Attachment.objects.get(id=request.POST.get('attachment_id', None), post_id=post_id)
            attachemnt.delete()

        except:
            # TODO: fix too broad exception
            pass

        return HttpResponse(status=204)


@login_required
def download_content(request: HttpRequest, post_id: int) -> HttpResponse:
    """Get all files of requested type for post_id and stream to client as ZIP archive

    :param request: Django request object
    :param post_id: post_id
    :return: Django HttpResponse with file
    """
    if request.method == 'GET':
        s = io.BytesIO()
        zipfile = ZipFile(s, 'w', ZIP_DEFLATED)
        attachments = Attachment.objects.filter(post_id=post_id, type=Attachment.TYPE_IMAGE).all()

        for attachment in attachments:
            fs_path = '%s/%s' % (settings.MEDIA_ROOT, attachment.file.name)
            filename = attachment.original_filename
            try:
                zipfile.write(fs_path, arcname=filename)
            except Exception as e:
                # TODO: handle not found files
                pass
        zipfile.close()

        resp = HttpResponse(s.getvalue(), content_type='application/x-zip-compressed')
        resp['Content-Disposition'] = f'attachment; filename=content_{post_id}.zip'
        return resp
