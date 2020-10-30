from magplan.models import Issue
import os
# from django.contrib.sites.models import Site


def inject_last_issues(request):
    issues = Issue.objects.order_by('-number').all()[:5]
    return {
        'navbar_issues': issues,
    }


def inject_app_url(request):
    # def current_site_failback():
    #     current_site = Site.objects.get_current()
    #     return current_site.domain

    return {
        'APP_URL': os.environ.get('APP_URL', None),
    }