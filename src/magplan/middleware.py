from django.utils import translation


class SetLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Set user language from settings
        try:
            user_language = request.user.user.preferences.get('magplan__ui_language')
            translation.activate(user_language)
            request.session[translation.LANGUAGE_SESSION_KEY] = user_language
        except:
            # HACK: should not raise I18n errors if Accept-Language
            # or settings is not configured
            pass

        response = self.get_response(request)

        return response
