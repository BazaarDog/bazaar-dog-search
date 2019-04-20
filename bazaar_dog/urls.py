"""bazaar_dog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.conf.urls import include, url
from ob.views import image, profile_image
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns

app_name = "bazaar-dog"

urlpatterns = [
    url(r'^logo.png', image, name='logo'),
    url(r'^logo_profile.png', profile_image, name='profile-logo'),

]

urlpatterns += i18n_patterns(
    url(r'', include('ob.api.urls', namespace='api-public')),
)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      url(r'^__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns
