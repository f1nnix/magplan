import datetime
import os
from typing import List, Tuple, Optional

import django_filters
import html2text
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.db.models import Count
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from magplan.conf import settings as config
from magplan.forms import CommentModelForm, IdeaModelForm, PostBaseModelForm, IDEA_AUTHOR_SELF_CHOICE
from magplan.models import Idea, Issue, Vote
from magplan.tasks.send_idea_comment_notification import send_idea_comment_notification
from magplan.tasks.send_idea_notification import send_idea_notification
from magplan.utils import safe_cast

IDEAS_PER_PAGE = 20

# HACK
AUTHOR_TYPE_DAY = datetime.date(2019, 6, 29)


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
            idea.editor = request.user.user
            idea.save()

            # Save authors, if existing specified
            if idea.author_type == Idea.AUTHOR_TYPE_EXISTING:
                form.save_m2m()

                # Handle virtual SELF choice (which is actual AUTHOR_TYPE_EXISTING)
                # We did it after actual m2m save as form.save_m2m()will overwrite any
                # model assignments usgin empty Form authors field. So saving one more time
                if request.POST.get('author_type') == IDEA_AUTHOR_SELF_CHOICE.slug:
                    idea.authors.add(request.user.user)
                    idea.save()

            send_idea_notification.delay(idea.id)

            messages.add_message(
                request, messages.SUCCESS,
                'Идея «%s» успешно выдвинута на голосование!' % idea.title)

            return redirect('ideas_show', idea_id=idea.id)

    form = IdeaModelForm()

    ideas = (Idea.objects
             .annotate(voted=Count("votes"))
             .prefetch_related('editor', )
             .order_by('-created_at'))

    # filters
    filter_ = request.GET.get('filter', None)
    if filter_ == 'voted':
        ideas = ideas.filter(approved=None)
    elif filter_ == 'self':
        ideas = ideas.filter(editor=request.user.user)
    elif filter_ == 'approved':
        ideas = ideas.filter(approved=True)
    elif filter_ == 'rejected':
        ideas = ideas.filter(approved=False)
    elif filter_ == 'no_author':
        ideas = ideas.filter(
            author_type=Idea.AUTHOR_TYPE_NO,
            created_at__gte=AUTHOR_TYPE_DAY,  # HACK
        )

    ideas = ideas.all()

    api_authors_search_url = reverse('api_authors_search')

    return render(request, 'magplan/ideas/index.html', {
        'ideas': ideas,
        'form': form,
        'filter_': filter_,
        'api_authors_search_url': api_authors_search_url
    })


def _get_suggestion_issues() -> Tuple[Optional[Issue], List[Issue]]:
    """Returns issues suggesion for "new Post" form.

    Retrieves five last opened issues, where last in array is newest
    """
    article_stages_for_opened_issues = (
        'waiting',
        'proofreading_editor',
        'precheck',
        'spellcheck',
        'markup',
        'proofreading_spell',
        'proofreading_chief_dpt',
        'proofreading_chief',
        'publishing',
    )
    opened_issues = \
        Issue.objects \
            .filter(posts__stage__slug__in=article_stages_for_opened_issues) \
            .order_by('number') \
            .distinct() \
            .all()[:5]

    if not opened_issues:
        return None, []

    # Convert QuerySet to ordinary list to split for initial and least
    opened_issues: List[Issue] = list(opened_issues)
    initial_issue = opened_issues.pop()
    opened_issues.reverse()

    return initial_issue, opened_issues


@login_required
def show(request, idea_id):
    idea = Idea.objects.prefetch_related('votes__user').get(id=idea_id)
    initial_issues_suggesion, issues_suggesions = _get_suggestion_issues()
    form = PostBaseModelForm(initial={
        'issues': initial_issues_suggesion,
        'finished_at': datetime.datetime.now() + datetime.timedelta(days=3),
    }, instance=idea)

    api_authors_search_url = reverse('api_authors_search')
    api_issues_search_url = reverse('api_issues_search')

    return render(request, 'magplan/ideas/show.html', {
        'idea': idea,
        'form': form,
        'issues_suggesions': issues_suggesions,
        'comment_form': CommentModelForm(),
        'AUTHOR_TYPE_CHOICES': Idea.AUTHOR_TYPE_CHOICES,
        'api_authors_search_url': api_authors_search_url,
        'api_issues_search_url': api_issues_search_url,
    })


@login_required
def vote(request, idea_id):
    DEFAULT_VOTE_SCORE = Vote.SCORE_50

    idea = Idea.objects.prefetch_related('votes__user').get(id=idea_id)
    vote = Vote(idea=idea, user=request.user.user)
    score: int

    if request.method == 'POST':
        score = request.POST.get('score', DEFAULT_VOTE_SCORE)
    else:
        score = request.GET.get('score', DEFAULT_VOTE_SCORE)

    score = safe_cast(score, to=int, on_error=DEFAULT_VOTE_SCORE)

    allowed_scored: List[int] = [
        score_choice[0] for score_choice in Vote.SCORE_CHOICES
    ]

    if score not in allowed_scored:
        score = Vote.SCORE_50

    vote.score = score
    vote.save()

    messages.add_message(request, messages.SUCCESS, 'Ваш голос учтен. Спасибо!')

    return redirect('ideas_show', idea_id=idea.id)


@login_required
def approve(request, idea_id):
    idea = Idea.objects.prefetch_related('votes__user').get(id=idea_id)

    if request.method == 'POST':
        idea.approved = (True if request.POST.get(
            'approve', False) == '1' else False)
        idea.save()
        messages.add_message(request, messages.INFO, 'Статус идеи изменен.')

        # send email
        if idea.approved is True and idea.editor != request.user.user:
            subject = f'Идея «{idea}» прошла голосование! Ждем статью'
            html_content = render_to_string('email/idea_approved.html', {
                'idea': idea,
                'APP_URL': os.environ.get('APP_URL', None),
            })
            text_content = html2text.html2text(html_content)
            msg = EmailMultiAlternatives(
                subject, text_content, config.PLAN_EMAIL_FROM, [idea.editor.email])
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
        comment.user = request.user.user

        if comment_form.is_valid():
            comment_form.save()

            send_idea_comment_notification.delay(comment.id)

            return redirect('ideas_show', idea.id)
    else:
        return redirect('ideas_show', idea.id)
