import datetime
import typing as tp

from django.contrib.auth.decorators import login_required
from django.db.models import Q, QuerySet
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.timezone import now

from magplan.forms import WhitelistedPostExtendedModelForm, AdPostExtendedModelForm, DefaultPostModelForm, \
    ArchivedPostModelForm
from magplan.models import Post, Stage, User
from magplan.utils import get_current_site


def _get_filtered_posts_queryset(filter_: tp.Optional[str], current_user: User, queryset: QuerySet = None) -> QuerySet:
    """
    Returns articles QuerySet, based on user request filters.
    """

    if queryset is None:
        queryset = Post.objects
    posts = queryset \
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


def get_api_urls() -> tp.Dict[str, str]:
    return {
        'api_authors_search_url': reverse('api_authors_search'),
        'api_issues_search_url': reverse('api_issues_search'),
    }


@login_required
def index(request):
    filter_ = request.GET.get('filter')

    current_context_site = get_current_site(request)
    queryset = Post.on_site(site=current_context_site)
    posts: QuerySet = _get_filtered_posts_queryset(
        filter_, request.user.user, queryset=queryset
    )

    # If user has any permissions to create any type of articles
    has_create_articles_permissions = any((
        request.user.has_perm('magplan.create_generic_post'),
        request.user.has_perm('magplan.create_archive_post'),
        request.user.has_perm('magplan.create_advert_post'),
        request.user.has_perm('magplan.create_regular_post'),
    ))

    return render(request, 'magplan/articles/index.html', {
        'posts': posts,
        'filter_': filter_,
        'has_create_articles_permissions': has_create_articles_permissions,
    })


@login_required
def default(request: HttpRequest):
    form = DefaultPostModelForm()

    if request.method == 'POST':
        form: Post = DefaultPostModelForm(request.POST)

        if form.is_valid():
            current_site = get_current_site(request)
            post: Post = form.save(commit=False)

            post.site = current_site
            post.editor = request.user.user
            post.stage = Stage.on_current_site.get(slug='waiting')

            post.save()
            form.save_m2m()

            return redirect('posts_show', post.id)

    return render(request, 'magplan/articles/default.html', {
        'form': form,
        **get_api_urls(),
    })


@login_required
def archived(request):
    form = ArchivedPostModelForm()

    if request.method == 'POST':
        form = ArchivedPostModelForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            post.editor = request.user.user
            post.stage = Stage.objects.get(slug='waiting')

            post.features = Post.POST_FEATURES_ARCHIVE

            post.save()
            form.save_m2m()

            return redirect('posts_show', post.id)

    return render(request, 'magplan/articles/archived.html', {
        'form': form,
        **get_api_urls(),
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

            post.features = Post.POST_FEATURES_ADVERT

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
