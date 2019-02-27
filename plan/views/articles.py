import datetime

from django.db.models import Q
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

from main.models import Post, Postype, Stage
from plan.forms import WhitelistedPostExtendedModelForm, AdPostExtendedModelForm


@login_required
def index(request):
    posts = Post.objects.order_by('-created_at').prefetch_related('section', 'stage', 'issues__magazine',
                                                                  'editor__profile')

    # filters
    filter = request.GET.get('filter', None)
    if filter == 'self':
        posts = posts.filter(editor=request.user)
    elif filter == 'overdue':
        posts = posts.filter(published_at__lte=datetime.datetime.now()).exclude(stage__slug='vault').exclude(
            stage__slug='published')
    elif filter == 'vault':
        posts = posts.filter(stage__slug='vault')
    else:
        posts = posts.all()

    posts = Paginator(posts, 25)  # Show 25 contacts per page

    page = request.GET.get('page')
    posts = posts.get_page(page)

    return render(request, 'plan/articles/index.html', {
        'posts': posts,
    })


@login_required
def whitelisted(request):
    form = WhitelistedPostExtendedModelForm()

    if request.method == 'POST':
        form = WhitelistedPostExtendedModelForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            post.editor = request.user
            post.postype = Postype.objects.get(slug='article')
            post.stage = Stage.objects.get(slug='waiting')

            post.save()
            form.save_m2m()

            return redirect('posts_show', post.id)

    return render(request, 'plan/articles/whitelisted.html', {
        'form': form,
    })


@login_required
def advert(request):
    form = AdPostExtendedModelForm()

    if request.method == 'POST':
        form = AdPostExtendedModelForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            post.editor = request.user
            post.postype = Postype.objects.get(slug='article')
            post.stage = Stage.objects.get(slug='waiting')

            post.save()

            form.cleaned_data['issues'] = [form.cleaned_data['issues']]  # HACK: cast object as list to support m2m
            form.save_m2m()

            return redirect('posts_show', post.id)

    return render(request, 'plan/articles/advert.html', {
        'form': form,
    })


@login_required
def search(request):
    if request.method == 'POST':
        q = request.POST['search_query']
        posts = (Post.objects
                 .prefetch_related('section', 'stage', 'issues__magazine', 'editor__profile')
                 .filter(Q(title__icontains=q) | Q(kicker__icontains=q)))

        return render(request, 'plan/articles/index.html', {
            'posts': posts,
            'q': q,
        })
