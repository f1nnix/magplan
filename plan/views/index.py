from django.shortcuts import render
from main.models import Post, Idea, Issue
from django.db.models import Q
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required
def index(request):
    self_posts = Post.objects.prefetch_related('stage').filter(
        Q(stage__assignee__isnull=False, stage__assignee=request.user, ) |
        Q(stage__assignee__isnull=True, editor=request.user, )
    ).exclude(stage__slug__in=['vault', 'published'])

    need_to_vote = Idea.objects.filter(approved__isnull=True).exclude(votes__user=request.user)

    # TODO: rewrite as negative query
    opened_issues = Issue.objects.filter(
        posts__stage__slug__in=['waiting', 'proofreading_editor', 'precheck', 'spellcheck', 'markup',
                                'proofreading_spell', 'proofreading_chief_dpt', 'proofreading_chief', 'publishing']) \
        .distinct()

    return render(request, 'plan/index/index.html', {
        'self_posts': self_posts,
        'need_to_vote': need_to_vote,
        'opened_issues': opened_issues,
    })
