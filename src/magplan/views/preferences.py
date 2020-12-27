from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from dynamic_preferences.users.forms import user_preference_form_builder


@login_required
def index(request):
    PreferencesForm = user_preference_form_builder(instance=request.user.user)
    if request.method == 'POST':
        form = PreferencesForm(request.POST)
        if form.is_valid():
            form.update_preferences()
            messages.add_message(
                request, messages.SUCCESS, "Настройи успешно обновлены"
            )

            return redirect('preferences_index')
        else:
            # TODO: check, if form reflects invalid
            #       payload for PreferencesForm
            PreferencesForm = user_preference_form_builder(instance=request.user.user)

    return render(request, 'magplan/preferences/index.html', {'form': PreferencesForm})
