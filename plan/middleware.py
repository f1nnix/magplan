from django.utils import translation


class SetLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Set user language from settings
        user_language = request.user.preferences.get('plan__ui_language')
        translation.activate(user_language)
        request.session[translation.LANGUAGE_SESSION_KEY] = user_language

        response = self.get_response(request)

        return response
