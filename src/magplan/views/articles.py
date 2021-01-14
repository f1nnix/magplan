import datetime
import typing as tp

from django.contrib.auth.decorators import login_required
from django.db.models import Q, QuerySet
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.timezone import now

from magplan.models import Post, Stage, User
from magplan.forms import WhitelistedPostExtendedModelForm, AdPostExtendedModelForm


def _get_filtered_posts_queryset(filter_: tp.Optional[str], current_user: User) -> QuerySet:
    """Returns articles QuerySet, based on user request filters.
    """
    posts = Post.objects \
        .prefetch_related('section', 'stage', 'issues__magazine', 'editor__profile') \
        .order_by('-updated_at')

    # Get filtered queryset
    if filter_ == 'self':
        posts = posts.filter(editor=current_user)
    elif filter_ == 'overdue':
        posts = posts \
            .filter(finished_at__lte=datetime.datetime.now()) \
            .exclude(stage__slug='vault') \
            .exclude(stage__slug='published')
    elif filter_ == 'vault':
        posts = posts.filter(stage__slug='vault')
    elif filter_ == 'all':
        # Don't apply any filters to get all posts
        pass
    else:
        # Render recent by default
        datetime_now = now()
        filter_kwargs = {
            'updated_at__gte': datetime_now - datetime.timedelta(2 * 30),
            'updated_at__lte': datetime_now,
        }
        posts = posts.filter(**filter_kwargs)

    return posts


@login_required
def index(request):
    filter_ = request.GET.get('filter')
    posts: QuerySet = _get_filtered_posts_queryset(filter_, request.user.user)
    return render(request, 'magplan/articles/index.html', {
        'posts': posts,
        'filter_': filter_,
    })


@login_required
def whitelisted(request):
    form = WhitelistedPostExtendedModelForm()

    if request.method == 'POST':
        form = WhitelistedPostExtendedModelForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            post.editor = request.user.user
            post.stage = Stage.objects.get(slug='waiting')

            post.save()
            form.save_m2m()

            return redirect('posts_show', post.id)

    api_authors_search_url = reverse('api_authors_search')
    api_issues_search_url = reverse('api_issues_search')

    return render(request, 'magplan/articles/whitelisted.html', {
        'form': form,
        'api_authors_search_url': api_authors_search_url,
        'api_issues_search_url': api_issues_search_url,
    })


@login_required
def advert(request):
    form = AdPostExtendedModelForm()

    if request.method == 'POST':
        form = AdPostExtendedModelForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            post.editor = request.user.user
            post.stage = Stage.objects.get(slug='waiting')

            post.save()

            form.cleaned_data['issues'] = [form.cleaned_data['issues']]  # HACK: cast object as list to support m2m
            form.save_m2m()

            return redirect('posts_show', post.id)

    api_authors_search_url = reverse('api_authors_search')

    return render(request, 'magplan/articles/advert.html', {
        'form': form,
        'api_authors_search_url': api_authors_search_url,
    })


@login_required
def search(request):
    if request.method == 'POST':
        q = request.POST['search_query']
        posts = (Post.objects
                 .prefetch_related('section', 'stage', 'issues__magazine', 'editor__profile')
                 .filter(Q(title__icontains=q) | Q(kicker__icontains=q)))

        return render(request, 'magplan/articles/index.html', {
            'posts': posts,
            'q': q,
        })
