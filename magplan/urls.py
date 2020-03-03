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
from django.contrib import admin
from django.urls import include, path  # For django versions from 2.0 and up
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required

from decorator_include import decorator_include


admin.site.site_header = 'Magplan'

urlpatterns = [
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
                  ] + urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
