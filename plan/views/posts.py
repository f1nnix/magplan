import os
import html2text
import datetime
from django.shortcuts import render, HttpResponse, redirect
from main.models import Post, Postype, Stage, Idea, Attachment, Comment, User
from plan.forms import PostBaseModelForm, PostExtendedModelForm, CommentModelForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from slugify import slugify
from constance import config
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from collections import deque


# Create your views here.
@login_required
def show(request, post_id):
    post = Post.objects.prefetch_related('editor', 'authors', 'stage', 'section', 'issues', 'comments__user').get(
        id=post_id)
    return render(request, 'plan/posts/show.html', {
        'post': post,
        'stages': Stage.objects.order_by('sort').all(),
        'form': CommentModelForm(),

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
        post.published_at = post.published_at + + datetime.timedelta(days=duration)
        post.stage = stage
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
