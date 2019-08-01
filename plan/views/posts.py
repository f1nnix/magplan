import datetime
import io
import os
from typing import List
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


def _create_system_comment(action_type, user, post, changelog=None, attachments=None, stage=None) -> Comment:
    """Create auto-generated system comment with post changes logs
    
    :param action_type:
    :param user:
    :param post:
    :param changelog:
    :return:
    """
    if not config.SYSTEM_USER_ID:
        return None

    if not attachments:
        attachments = ()
    if not stage:
        stage = post.stage

    system_user = User.objects.get(id=config.SYSTEM_USER_ID)
    comment = Comment()
    comment.commentable = post
    comment.type = Comment.TYPE_SYSTEM
    comment.user = system_user

    # Depending on action type, fill different fields
    meta = {
        'action': action_type,
        'user': {
            'id': user.id,
            'str': user.__str__(),
        },
        'files': [],

    }

    if action_type == Comment.SYSTEM_ACTION_CHANGE_META:
        meta['changelog'] = changelog

    elif action_type == Comment.SYSTEM_ACTION_UPDATE:
        if len(attachments) > 0:
            meta['files'] = [{
                'id': a.id,
                'str': a.original_filename
            } for a in attachments]

    elif action_type == Comment.SYSTEM_ACTION_SET_STAGE:
        meta['stage'] = {
            'id': post.stage.id,
            'str': post.stage.__str__(),
        }

    # Assign builded meta to comment and save
    comment.meta['comment'] = meta
    comment.save()

    return comment


def _generate_changelog_for_form(form: PostMetaForm) -> List[str]:
    """Iterate over all changed attributes and stage changes in logs

    :param form: Django form
    :return: list, where each element is changelog line
    """
    changelog = []
    changed_fields = form.changed_data.copy()
    changed_fields.remove('wp_id')

    __ = lambda form, field: (
        ', '.join([str(i) for i in form.initial.get(field)]),
        ', '.join([str(i) for i in form.cleaned_data.get(field)])
    )
    _ = lambda form, field: (
        form.initial.get(field),
        form.cleaned_data.get(field)
    )
    for changed_field in changed_fields:
        log = None

        if changed_field == 'issues':
            log = '* выпуски сменились с "{0}" на "{1}"'.format(*__(form, changed_field))
        elif changed_field == 'editor':
            # Initial ForeignKey value is stored as int. Populate it
            args = _(form, changed_field)
            init_editor = str(User.objects.get(id=args[0]))
            new_args = (init_editor, args[1])
            log = '* редактор cменился с "{0}" на "{1}"'.format(*new_args)
        elif changed_field == 'finished_at':
            log = '* дедлайн этапа cменился с "{0}" на "{1}"'.format(*_(form, changed_field))
        elif changed_field == 'published_at':
            log = '* дата публикации сменилась с "{0}" на "{1}"'.format(*_(form, changed_field))

        if log:
            changelog.append(log)

    return changelog


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

            _create_system_comment(Comment.SYSTEM_ACTION_UPDATE, request.user, post,
                                   attachments=attachments)

            messages.add_message(request, messages.SUCCESS, 'Пост «%s» успешно отредактирован' % post)

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
    def _get_value_repr(value) -> str:
        try:
            iter(value)
            return ', '.join(list(map(str(o) for o in value)))
        except TypeError as te:
            return str(value)

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return HttpResponse(status=401)

    if request.method == 'POST':
        form = PostMetaForm(request.POST, instance=post)
        if not form.is_valid():
            return HttpResponse(status=403)

        # Manually set new Wordpress ID as it's ignored by form
        form.instance.meta['wpid'] = form.cleaned_data.get('wp_id')

        published_at = form.cleaned_data.get('published_at')
        if published_at:
            dt = published_at.replace(hour=10, minute=0, second=0)
            form.instance.published_at = dt

        form.save()

        # Create system comment with changelog
        changelog = _generate_changelog_for_form(form)
        if len(changelog) > 0:
            _create_system_comment(Comment.SYSTEM_ACTION_CHANGE_META, request.user, post, changelog)

        messages.add_message(request, messages.INFO, f'Пост {post} успешно обновлен!')

    return redirect('posts_show', post_id)


@login_required
@permission_required('main.edit_extended_post_attrs')
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

        # Create system comment
        _create_system_comment(Comment.SYSTEM_ACTION_SET_STAGE, request.user, post,
                               stage=post.stage)

        # Send email if stage allows it
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
