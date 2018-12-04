from django.shortcuts import render
from main.models import Issue
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required
def index(request):
    issues = Issue.objects.all().order_by('-number').prefetch_related('magazine')

    return render(request, 'plan/issues/index.html', {
        'issues': issues,
    })


@login_required
def show(request, issue_id):
    issue = Issue.objects.get(id=issue_id)
    posts = issue.posts.all().order_by('section__sort').prefetch_related('authors', 'editor', 'stage',
                                                                         'section').exclude(stage__slug='vault')

    return render(request, 'plan/issues/show.html', {
        'issue': issue,
        'posts': posts,
        'stats': {
            'has_text': len(list(filter(lambda p: (p.xmd is not None) and (p.xmd != ''), posts))),
            'incomplete': len(list(filter(lambda p: p.stage.slug != 'published', posts))),
        }
    })
