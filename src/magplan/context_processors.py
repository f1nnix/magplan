import os

from django.contrib.sites.models import Site

from magplan.models import Issue


def inject_last_issues(request):
    issues = Issue.objects.order_by('-number').all()[:5]
    return {
        'navbar_issues': issues,
    }


def inject_app_url(request):
    return {
        'APP_URL': os.environ.get('APP_URL', None),
    }


def inject_sites(request):
    current_site: Site = Site.objects.get_current(request=request)
    return {
        'current_site': current_site,
        'sites': Site.objects.exclude(id=current_site.id),
    }
