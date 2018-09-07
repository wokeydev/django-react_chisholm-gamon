from django.conf.urls import url
from . import views

app_name = "enquiries"

urlpatterns = [
    url(r'listing-enquiries/create/$', views.CreateListingEnquiryApi.as_view(), name="listing_enquiry_create"),
    url(r'page-enquiries/create/$', views.CreatePageEnquiryAPI.as_view(), name="page_enquiry_create")
]
