import html2text
import django_filters
import os
from django.shortcuts import render, redirect
from main.models import Idea, Vote, Issue, User
from plan.forms import IdeaModelForm, PostBaseModelForm, CommentModelForm
from django.db.models import Count
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from constance import config


class IdeaApprovedFilter(django_filters.FilterSet):
    approved = django_filters.BooleanFilter(field_name='approved')

    class Meta:
        model = Idea
        fields = ['approved', ]


@login_required
def index(request):
    if request.method == 'POST':
        form = IdeaModelForm(request.POST)
        if form.is_valid():
            idea = form.save(commit=False)
            idea.editor = request.user
            idea.save()
            messages.add_message(request, messages.SUCCESS, 'Идея «%s» успешно выдвинута на голосование!' % idea.title)
    else:
        form = IdeaModelForm()

    ideas = (Idea.objects
             .annotate(voted=Count("votes"))
             .prefetch_related('editor', )
             .order_by('-created_at'))

    # filters
    filter = request.GET.get('filter', None)
    if filter == 'voted':
        ideas = ideas.filter(approved=None).all()
    elif filter == 'self':
        ideas = ideas.filter(editor=request.user).all()
    elif filter == 'approved':
        ideas = ideas.filter(approved=True).all()
    elif filter == 'rejected':
        ideas = ideas.filter(approved=False).all()
    else:
        ideas = ideas.all()

    paginator = Paginator(ideas, 10)
    page = request.GET.get('page')
    ideas_paginated = paginator.get_page(page)

    return render(request, 'plan/ideas/index.html', {
        'ideas': ideas_paginated,
        'form': form,
        'filter_': filter,
    })


@login_required
def show(request, idea_id):
    idea = Idea.objects.prefetch_related('votes__user').get(id=idea_id)
    form = PostBaseModelForm(initial={
        'issues': Issue.objects.order_by('-number').first(),
        # 'authors': User.objects.last(),
    }, instance=idea)

    return render(request, 'plan/ideas/show.html', {
        'idea': idea,
        'form': form,
        'comment_form': CommentModelForm(),
    })


@login_required
def vote(request, idea_id):
    idea = Idea.objects.prefetch_related('votes__user').get(id=idea_id)

    if request.method == 'POST':
        vote = Vote(score=request.POST.get('score', 1), idea=idea, user=request.user)
        vote.save()
        messages.add_message(request, messages.SUCCESS, 'Ваш голос учтен. Спасибо!')

    return redirect('ideas_show', idea_id=idea.id)


@login_required
def approve(request, idea_id):
    idea = Idea.objects.prefetch_related('votes__user').get(id=idea_id)

    if request.method == 'POST':
        idea.approved = (True if request.POST.get('approve', False) == '1' else False)
        idea.save()
        messages.add_message(request, messages.INFO, 'Статус идеи изменен.')

        # send email
        if idea.approved is True and idea.editor != request.user:
            subject = f'Идея «{idea}» прошла голосование! Ждем статью'
            html_content = render_to_string('email/idea_approved.html', {
                'idea': idea,
                'APP_URL': os.environ.get('APP_URL', None),
            })
            text_content = html2text.html2text(html_content)
            msg = EmailMultiAlternatives(subject, text_content, config.PLAN_EMAIL_FROM, [idea.editor.email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

    return redirect('ideas_show', idea_id=idea.id)


@login_required
def comments(request, idea_id):
    idea = Idea.objects.prefetch_related('votes__user').get(id=idea_id)
    if request.method == 'POST':
        comment_form = CommentModelForm(request.POST)

        comment = comment_form.save(commit=False)
        comment.commentable = idea
        comment.user = request.user

        if comment_form.is_valid():
            comment_form.save()

            # send email
            # send notification to:
            #   * all, who has 'recieve_admin_emails' permission
            #   * post editor
            recipients = [u.email for u in User.objects.filter(groups__name='Editors').exclude(id=comment.user.id)]

            if idea.editor != request.user:
                recipients.append(idea.editor.email)

            if len(recipients) > 0:
                subject = f'Комментарий к идее «{idea}» от {comment.user}'
                html_content = render_to_string('email/new_comment.html', {
                    'comment': comment,
                    'commentable_type': 'post' if comment.commentable.__class__.__name__ == 'Post' else 'idea',
                    'APP_URL': os.environ.get('APP_URL', None),
                })
                text_content = html2text.html2text(html_content)
                msg = EmailMultiAlternatives(subject, text_content, config.PLAN_EMAIL_FROM, recipients)
                msg.attach_alternative(html_content, "text/html")
                msg.send()

            return redirect('ideas_show', idea.id)
    else:
        return redirect('ideas_show', idea.id)
