from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'(?P<slug>[-\w]+)/', views.TestimonialView.as_view(), name="testimonial_details_slug")
]
