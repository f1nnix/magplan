from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from dynamic_preferences.users.forms import user_preference_form_builder


@login_required
def index(request):
    PreferencesForm = user_preference_form_builder(instance=request.user)
    if request.method == 'POST':
        form = PreferencesForm(request.POST)
        if form.is_valid():
            form.update_preferences()
            return redirect('preferences_index')
        else:
            # TODO: check, if form reflects invalid
            #       payload for PreferencesForm
            PreferencesForm = user_preference_form_builder(instance=request.user)

    return render(request, 'plan/preferences/index.html', {
        'form': PreferencesForm
    })
