from typing import Any, Callable

from django.conf import settings
from django.contrib.sites.models import Site
from django.http import HttpRequest


def safe_cast(value: Any, to: Callable, on_error: Any = None) -> Any:
    """ "Safe casts value to type with provided casting constructor.

    If cast falls for some reason, default on_error value is returned.*

    :param value: Source value to cast*
    :param to: Callable constructor, which can accept typed value*
    :param on_error: Value to return is cast falls: bad constructor, unacceptable source type*
     :return: casted value or fallback*
    """
    try:
        casted: Any = to(value)
    except (ValueError, TypeError):  # noqa
        return on_error

    return casted


def get_current_site(request: HttpRequest, safe: bool = True) -> Site:
    """
    Returns selected on plan site from user settings
    """
    current_site_id = request.user.preferences["magplan__current_site"]  # noqa
    if current_site_id:
        try:
            Site.objects.get(id=current_site_id)
        except Site.DoesNotExist:
            pass  # FIXME

    DEFAULT_SITE_ID: int = settings.SITE_ID

    # Should exists, don't handle exceptions
    return Site.objects.get(id=DEFAULT_SITE_ID)
