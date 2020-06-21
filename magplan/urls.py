"""magplan URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from authtools import views as authtools_views
from decorator_include import decorator_include
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import include, path  # For django versions from 2.0 and up

admin.site.site_header = 'Plan'

urlpatterns = [
    url(
        r'accounts/password_reset/$',
        authtools_views.PasswordResetView.as_view(domain_override=settings.APP_HOST),
        name='password_reset'
    ),
    path('accounts/', include('authtools.urls')),

    path('admin/', include('plan.urls')),
    path('manage/', admin.site.urls),

    path('notifications/', include('django_nyt.urls')),
    path('wiki/', decorator_include(login_required, 'wiki.urls')),
    path('', include('main.urls')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      path('__debug__/', include(debug_toolbar.urls)),
                      path('django_mail_viewer/', include('django_mail_viewer.urls')),
                  ] + urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
