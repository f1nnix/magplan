import datetime
import io
import os
from typing import List, Optional
from zipfile import ZIP_DEFLATED, ZipFile

import html2text
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.http import HttpRequest, HttpResponseForbidden
from django.shortcuts import HttpResponse, redirect, render
from django.shortcuts import get_object_or_404
from django.template import Context, Template
from django.template.loader import render_to_string
from django.urls import reverse
from magplan.conf import settings as config
from magplan.forms import (
    CommentModelForm,
    PostBaseModelForm,
    PostExtendedModelForm,
    PostMetaForm,
)
from magplan.models import (
    Attachment,
    Comment,
    Idea,
    Post,
    Stage,
    User,
)
from magplan.tasks.send_post_comment_notification import send_post_comment_notification
from magplan.tasks.upload_post_to_wp import upload_post_to_wp
from slugify import slugify

IMAGE_MIME_TYPE_JPEG= 'image/jpeg'
IMAGE_MIME_TYPES = {
    'image/gif',
    IMAGE_MIME_TYPE_JPEG,
    'image/png',
}


def _get_arbitrary_chunk(post: Post) -> str:
    """Render instance specific template code

    Used to render some arbitrary HTML code in a context of Post instance.
    Useful to provide sensitive HTML template, which can't be committed
    into Git repository directly or may vary for each particular instance.

    :param post: Post instance to use in template
    :return: Rendered template string
    """
    instance_template = Template(config.PLAN_POSTS_INSTANCE_CHUNK)
    instance_chunk = instance_template.render(Context({"post": post}))
    return instance_chunk


def _create_system_comment(
        action_type, user, post, changelog=None, attachments=None, stage=None
) -> Comment:
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
        "action": action_type,
        "user": {"id": user.id, "str": user.__str__()},
        "files": [],
    }

    if action_type == Comment.SYSTEM_ACTION_CHANGE_META:
        meta["changelog"] = changelog

    elif action_type == Comment.SYSTEM_ACTION_UPDATE:
        if len(attachments) > 0:
            meta["files"] = [
                {"id": a.id, "str": a.original_filename} for a in attachments
            ]

    elif action_type == Comment.SYSTEM_ACTION_SET_STAGE:
        meta["stage"] = {"id": post.stage.id, "str": post.stage.__str__()}

    # Assign builded meta to comment and save
    comment.meta["comment"] = meta
    comment.save()

    return comment


def _generate_changelog_for_form(form: PostMetaForm) -> List[str]:
    """Iterate over all changed attributes and stage changes in logs

    :param form: Django form
    :return: list, where each element is changelog line
    """
    changelog = []
    changed_fields = form.changed_data.copy()
    if "wp_id" in changed_fields:
        changed_fields.remove("wp_id")

    __ = lambda form, field: (
        ", ".join([str(i) for i in form.initial.get(field)]),
        ", ".join([str(i) for i in form.cleaned_data.get(field)]),
    )
    _ = lambda form, field: (form.initial.get(field), form.cleaned_data.get(field))
    for changed_field in changed_fields:
        log = None

        if changed_field == "issues":
            log = '* выпуски сменились с "{0}" на "{1}"'.format(
                *__(form, changed_field)
            )
        elif changed_field == "editor":
            # Initial ForeignKey value is stored as int. Populate it
            args = _(form, changed_field)
            init_editor = str(User.objects.get(id=args[0]))
            new_args = (init_editor, args[1])
            log = '* редактор cменился с "{0}" на "{1}"'.format(*new_args)
        elif changed_field == "finished_at":
            log = '* дедлайн этапа cменился с "{0}" на "{1}"'.format(
                *_(form, changed_field)
            )
        elif changed_field == "published_at":
            log = '* дата публикации сменилась с "{0}" на "{1}"'.format(
                *_(form, changed_field)
            )

        if log:
            changelog.append(log)

    return changelog


def _authorize_stage_change(user: User, post: Post, new_stage_id: int) -> bool:
    """Check if user is authorized to set stage for post

    :param user: User instance
    :param post: Post instance
    :param new_stage_id: Stage to to set for post
    :return: True if authorized, otherwise False
    """
    legit_stages = (post.stage.prev_stage_id, post.stage.next_stage_id)

    if new_stage_id in legit_stages and post.assignee == user:
        return True

    if user.has_perm("magplan.edit_extended_post_attrs"):
        return True

    return False


def _save_attachments(
        files: List, post: Post, user: User,
        featured_image_file: Optional = None
) -> List[Attachment]:
    attachments = []

    with transaction.atomic():
        for file in files:
            # Delete files with the same filename,
            # uploaded for current post. Emulates overwrite without
            # custom FileSystemStorage
            Attachment.objects.filter(
                post=post, original_filename=file.name
            ).delete()

            attachment = Attachment(
                post=post, user=user, original_filename=file.name
            )  # save original filename

            # Slugify original filename and save with safe one
            filename, extension = os.path.splitext(file.name)
            file.name = "%s%s" % (slugify(filename), extension)

            # Assign file object with slugified filename as name,
            # original is copied by value
            attachment.file = file

            if file.content_type in IMAGE_MIME_TYPES:
                attachment.type = Attachment.TYPE_IMAGE
            elif file.content_type == "application/pdf":
                attachment.type = Attachment.TYPE_PDF
            else:
                attachment.type = Attachment.TYPE_FILE

            attachment.save()
            attachments.append(attachment)

        # This can be spoofed on client_side
        if featured_image_file and featured_image_file.content_type == IMAGE_MIME_TYPE_JPEG:
            # Delete any previously uploaded featured images
            Attachment.objects.filter(
                post=post, type=Attachment.TYPE_FEATURED_IMAGE
            ).delete()

            attachment = Attachment(
                post=post,
                user=user,
                original_filename=featured_image_file.name,
                type=Attachment.TYPE_FEATURED_IMAGE,
                file=featured_image_file,
            )  # save original filename

            attachment.save()


    return attachments


@login_required
def show(request, post_id):
    post = Post.objects.prefetch_related(
        "editor", "authors", "stage", "section", "issues", "comments__user"
    ).get(id=post_id)

    post_meta_form = PostMetaForm(
        initial={
            'wp_id': post.meta.get('wpid')
        },
        instance=post
    )

    api_issues_search_url = reverse('api_issues_search')

    return render(
        request,
        "magplan/posts/show.html",
        {
            "post": post,
            "stages": Stage.on_current_site.order_by("sort").all(),
            "instance_chunk": _get_arbitrary_chunk(post),
            "comment_form": CommentModelForm(),
            "meta_form": post_meta_form,
            "TYPE_CHOICES": Comment.TYPE_CHOICES,
            "SYSTEM_ACTION_CHOICES": Comment.SYSTEM_ACTION_CHOICES,
            'api_issues_search_url': api_issues_search_url,

        },
    )


@login_required
def create(request):
    if request.method == "POST":
        form: Post = PostBaseModelForm(request.POST)

        # Set post site scope
        if form.is_valid():
            post = form.save(commit=False)
            post.editor = request.user.user
            post.stage = Stage.objects.get(slug="waiting")

            post.save()
            form.save_m2m()

            idea = Idea.objects.get(id=request.POST.get("idea_id", None))
            idea.post = post
            idea.save()

            return redirect("posts_show", post.id)

    else:
        return HttpResponse(status=405)


@login_required
def edit(request, post_id):
    post = Post.objects.prefetch_related(
        "editor", "authors", "stage", "section", "issues"
    ).get(id=post_id)

    if request.method == "POST":
        form = PostExtendedModelForm(request.POST, request.FILES, instance=post)

        attachments_files = request.FILES.getlist("attachments")
        featured_image_files = request.FILES.getlist('featured_image')
        attachments = _save_attachments(
            attachments_files, post, request.user.user,
            featured_image_file=(
                featured_image_files[0] if featured_image_files else None
            )
        )

        if form.is_valid():
            post.imprint_updater(request.user.user)
            form.save()

            _create_system_comment(
                Comment.SYSTEM_ACTION_UPDATE,
                request.user.user,
                post,
                attachments=attachments,
            )
            messages.add_message(
                request, messages.SUCCESS, "Пост «%s» успешно отредактирован" % post
            )

            return redirect("posts_edit", post_id)

        else:
            messages.add_message(
                request, messages.ERROR, "При обновлении поста произошла ошибка ввода"
            )

    else:
        form = PostExtendedModelForm(instance=post)

    api_authors_search_url = reverse('api_authors_search')

    return render(request, "magplan/posts/edit.html", {
        "post": post,
        "form": form,
        'api_authors_search_url': api_authors_search_url
    })


@login_required
def edit_meta(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return HttpResponse(status=401)

    if request.method == "POST":
        form = PostMetaForm(request.POST, instance=post)
        if not form.is_valid():
            return HttpResponse(status=403)

        # Manually set new Wordpress ID as it's ignored by form
        form.instance.meta["wpid"] = form.cleaned_data.get("wp_id")

        published_at = form.cleaned_data.get("published_at")
        if published_at:
            dt = published_at.replace(hour=10, minute=0, second=0)
            form.instance.published_at = dt

        form.save()

        # Create system comment with changelog
        changelog = _generate_changelog_for_form(form)
        if len(changelog) > 0:
            _create_system_comment(
                Comment.SYSTEM_ACTION_CHANGE_META, request.user.user, post, changelog
            )

        messages.add_message(request, messages.INFO, f"Пост {post} успешно обновлен!")

    return redirect("posts_show", post_id)


@login_required
def set_stage(request, post_id, system=Comment.TYPE_SYSTEM):
    post = Post.objects.prefetch_related("stage__n_stage", "stage__p_stage").get(
        id=post_id
    )

    if request.method == "POST" and request.POST.get("new_stage_id"):
        if not _authorize_stage_change(
                request.user.user, post, int(request.POST.get("new_stage_id"))
        ):
            return HttpResponseForbidden()

        stage = Stage.objects.get(id=request.POST.get("new_stage_id", None))

        # set deadline to current stage durtion. If no duration, append 1 day
        duration = stage.duration if stage.duration else 1
        post.finished_at = post.finished_at + +datetime.timedelta(days=duration)
        post.stage = stage
        post.imprint_updater(request.user.user)
        post.save()
        messages.add_message(
            request, messages.INFO, "Текущий этап статьи «%s» обновлен" % post
        )

        # Create system comment
        _create_system_comment(
            Comment.SYSTEM_ACTION_SET_STAGE, request.user.user, post, stage=post.stage
        )

        # TODO: extract method
        # Send email if stage allows it
        if post.assignee != request.user.user and stage.skip_notification is False:
            subject = f"На вас назначена статья «{post}»"
            html_content = render_to_string(
                "email/assigned_to_you.html",
                {"post": post, "APP_URL": os.environ.get("APP_URL", None)},
            )
            text_content = html2text.html2text(html_content)
            msg = EmailMultiAlternatives(
                subject, text_content, config.PLAN_EMAIL_FROM, [post.assignee.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            return redirect("posts_show", post_id)

    return redirect("posts_show", post.id)


@login_required
def comments(request, post_id):
    post = Post.objects.prefetch_related(
        "editor", "authors", "stage", "section", "issues", "comments__user"
    ).get(id=post_id)

    if request.method == "POST":
        form = CommentModelForm(request.POST)

        comment = form.save(commit=False)
        comment.commentable = post
        comment.user = request.user.user

        if form.is_valid():
            form.save()

            # Send notification to users with 'recieve_post_email_updates' permission
            send_post_comment_notification.delay(comment.id)
            return redirect("posts_show", post_id)

    return render(
        request,
        "magplan/posts/show.html",
        {
            "post": post,
            "stages": Stage.objects.order_by("sort").all(),
            "form": CommentModelForm(),
        },
    )


@login_required
def attachment_delete(request, post_id):
    if request.method == "POST":
        try:
            attachemnt = Attachment.objects.get(
                id=request.POST.get("attachment_id", None), post_id=post_id
            )
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
    if request.method == "GET":
        s = io.BytesIO()
        zipfile = ZipFile(s, "w", ZIP_DEFLATED)
        attachments = Attachment.objects.filter(
            post_id=post_id, type=Attachment.TYPE_IMAGE
        ).all()

        for attachment in attachments:
            fs_path = "%s/%s" % (settings.MEDIA_ROOT, attachment.file.name)
            filename = attachment.original_filename
            try:
                zipfile.write(fs_path, arcname=filename)
            except Exception as e:
                # TODO: handle not found files
                pass
        zipfile.close()

        resp = HttpResponse(s.getvalue(), content_type="application/x-zip-compressed")
        resp["Content-Disposition"] = f"attachment; filename=content_{post_id}.zip"
        return resp


def send_to_wp(request: HttpRequest, post_id: int) -> HttpResponse:
    if request.method == "GET":
        post = get_object_or_404(Post, id=post_id)
        upload_post_to_wp.delay(post.id)

        messages.add_message(
            request, messages.INFO, "Пост «%s» отправлен в Wordpress" % post
        )

        return redirect("posts_show", post.id)
