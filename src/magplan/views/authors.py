from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.db.models import Q
from django.shortcuts import render, redirect

from magplan.models import User, Post
from magplan.forms import UserModelForm, ProfileModelForm


@login_required
@permission_required('magplan.manage_authors')
def index(request):
    users = User.objects.prefetch_related('profile').order_by('profile__l_name').all()
    return render(request, 'magplan/authors/index.html', {
        'users': users
    })


@login_required
@permission_required('magplan.manage_authors')
def new(request):
    if request.method == 'POST':
        user_form = UserModelForm(request.POST)
        profile_form = ProfileModelForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            # Authors should be inactive by default
            user.is_active = False
            user.save()

            profile_form = ProfileModelForm(request.POST, instance=user.profile)
            profile_form.save()

            messages.add_message(request, messages.INFO, f'Автор «{user}» успешно создан')

            return redirect('authors_edit', user.id)

    else:
        user_form = UserModelForm()
        profile_form = ProfileModelForm()

    return render(request, 'magplan/authors/new.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })


@login_required
@permission_required('magplan.manage_authors')
def show(request, user_id):
    user = User.objects.get(id=user_id)
    posts = (Post.objects.filter(Q(authors=user) | Q(editor=user))
             .prefetch_related('authors', 'editor', 'stage', 'section')
             .exclude(stage__slug='vault')
             .order_by('created_at'))
    return render(request, 'magplan/authors/show.html', {
        'user': user,
        'posts': posts,
    })


@login_required
@permission_required('magplan.manage_authors')
def edit(request, user_id):
    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        user_form = UserModelForm(request.POST, instance=user)
        profile_form = ProfileModelForm(request.POST, instance=user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            messages.add_message(request, messages.INFO, f'Автор «{user}» успешно отредактирован')

    else:
        user_form = UserModelForm(instance=user)
        profile_form = ProfileModelForm(instance=user.profile)

    return render(request, 'magplan/authors/edit.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'user': user,
    })
