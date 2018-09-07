from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.ListingSearchView.as_view(), name="listing_search"),
    url(r'^autocomplete/$', views.ListingAutocompleteView.as_view(), name="listing_autocomplete"),
    url(r'^upcoming-auctions/$', views.ListingAuctionSearchView.as_view(), name="listing_auction_search"),
    url(r'^upcoming-inspections/$', views.ListingInspectionSearchView.as_view(), name="listing_inspections_search"),
    url(r'(?P<slug>[-\w]+)-(?P<pk>\d+)/', views.ListingDetailView.as_view(), name="listing_details")
]
