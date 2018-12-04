from django.shortcuts import render, redirect
from main.models import User
from django.contrib.auth.decorators import login_required
from plan.forms import UserModelForm, ProfileModelForm
from django.contrib import messages


@login_required
def index(request):
    users = User.objects.prefetch_related('profile').order_by('profile__l_name').all()
    return render(request, 'plan/authors/index.html', {
        'users': users
    })


@login_required
def new(request):
    if request.method == 'POST':
        user_form = UserModelForm(request.POST)
        profile_form = ProfileModelForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            profile_form = ProfileModelForm(request.POST, instance=user.profile)
            profile_form.save()

            messages.add_message(request, messages.INFO, f'Автор «{user}» успешно создан')

            return redirect('authors_edit', user.id)

    else:
        user_form = UserModelForm()
        profile_form = ProfileModelForm()

    return render(request, 'plan/authors/new.html', {
        'user_form': user_form,
        'profile_form': profile_form,
    })


@login_required
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

    return render(request, 'plan/authors/edit.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'user': user,
    })
