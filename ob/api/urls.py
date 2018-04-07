from django.conf.urls import url

from .views import *

app_name="listing"

urlpatterns = [

    url(r'report/', Report.as_view(), name='report-listing'),
    url(r'profile/', ProfileSearch.as_view(), name='profile-page'),
    url(r'listing/', ListingSearch.as_view(), name='listing-page'),
    url(r'', ListingSearch.as_view(), name='listing-page'),
]
