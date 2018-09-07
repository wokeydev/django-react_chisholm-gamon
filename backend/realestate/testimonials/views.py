from django.shortcuts import render
from django.views.generic import DetailView
from .models import Testimonial


class TestimonialView(DetailView):
    model = Testimonial
    template_name = 'testimonials/testimonial_details.html'