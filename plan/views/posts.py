import datetime
import io
import os
from collections import deque
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

from main.models import Post, Postype, Stage, Idea, Attachment, Comment, User
from plan.forms import PostBaseModelForm, PostExtendedModelForm, CommentModelForm


# Create your views here.
@login_required
def show(request, post_id):
    post = Post.objects.prefetch_related('editor', 'authors', 'stage', 'section', 'issues', 'comments__user').get(
        id=post_id)

    # redner instance specific template code
    intance_template = Template(config.PLAN_POSTS_INSTANCE_CHUNK)
    instance_chunk = intance_template.render(Context({
        'post': post,
    }))
    pass
    return render(request, 'plan/posts/show.html', {
        'post': post,
        'stages': Stage.objects.order_by('sort').all(),
        'form': CommentModelForm(),
        'instance_chunk': instance_chunk,

        'TYPE_SYSTEM': Comment.TYPE_SYSTEM,
        'SYSTEM_ACTION_SET_STAGE': Comment.SYSTEM_ACTION_SET_STAGE,
        'SYSTEM_ACTION_UPDATE': Comment.SYSTEM_ACTION_UPDATE,
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
            pass
            # import pdb;
            # pdb.set_trace()

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

        attachments = deque()
        for file in files:
            attachment = Attachment(post=post, user=request.user, original_filename=file.name)  # save original filename

            # slugify original filename and save with safe one
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
@permission_required('main.schedule_publish')
def schedule(request, post_id):
    post = Post.objects.get(id=post_id)

    published_at = request.POST.get('published_at')
    if published_at is None:
        messages.add_message(request, messages.ERROR, 'Ошибка планирования публикации — дата не передана')
        return redirect('posts_show', post.id)

    post.published_at = published_at
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

            # send email
            # send notification to:
            #   * all, who has 'recieve_admin_emails' permission
            #   * post editor
            recipients = [u.email for u in User.objects.filter(groups__name='Editors').exclude(id=comment.user.id)]

            if post.editor != request.user:
                recipients.append(post.editor.email)

            if len(recipients) > 0:
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
        attachemnts = Attachment.objects.filter(post_id=post_id, type=Attachment.TYPE_IMAGE).all()

        for attachemnt in attachemnts:
            fs_path = '%s/%s' % (settings.MEDIA_ROOT, attachemnt.file.name)
            filename = attachemnt.original_filename
            try:
                zipfile.write(fs_path, arcname=filename)
            except Exception as e:
                # TODO: handle not found files
                pass
        zipfile.close()

        resp = HttpResponse(s.getvalue(), content_type='application/x-zip-compressed')
        resp['Content-Disposition'] = f'attachment; filename=content_{post_id}.zip'
        return resp
