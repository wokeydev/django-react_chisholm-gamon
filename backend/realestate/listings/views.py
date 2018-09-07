from collections import defaultdict
from django.views.generic import FormView, DetailView
from django.views.generic.edit import FormMixin
from django.core.paginator import Paginator
from django.http import JsonResponse
from wagtail.search.backends import get_search_backend

from .forms import ListingInspectionSearchForm, ListingAuctionSearchForm, ListingSearchForm
from realestate.enquiries.forms import ListingEnquiryForm
from .settings import DEFAULT_PER_PAGE
from .models import PropertyListing

try:
    from realestate.agents.models import AgentPage
except ImportError:
    AgentPage = None

try:
    from schools.models import School
except ImportError:
    School = None


class ListingSearchView(FormView):
    form_class = ListingSearchForm
    per_page = DEFAULT_PER_PAGE
    per_page_kwarg = 'per_page'
    page_kwarg = 'page'
    template_name = "listings/search.html"

    def get_per_page(self):
        return self.kwargs.get('per_page', DEFAULT_PER_PAGE)

    def get_page_number(self):
        return self.kwargs.get(self.page_kwarg, 1)

    def get_form_kwargs(self):
        kwargs = super(ListingSearchView, self).get_form_kwargs()
        kwargs['initial'] = kwargs['initial'].update(self.kwargs)
        kwargs['data'] = self.request.GET.copy()
        return kwargs

    def get_listings(self):
        return self.get_form().as_search()

    def get_context_data(self, **kwargs):
        context = super(ListingSearchView, self).get_context_data(**kwargs)
        listing_paginator = Paginator(self.get_listings(), self.get_per_page())
        context['listings'] = listing_paginator.get_page(self.get_page_number())
        context['form'] = self.get_form()
        if context['form'].data.get('agent') and AgentPage:
            try:
                context['agent'] = AgentPage.objects.get(pk=context['form'].data.get('agent'))
            except AgentPage.DoesNotExist:
                pass
        return context


class ListingAutocompleteView(ListingSearchView):
    """
    JSON Response view to be used for autocomplete
    """
    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)

    def get_context_data(self, **kwargs):
        context = {}
        if not self.request.GET.keys():
            # We don't want people spamming for full result sets
            return context

        listings = self.get_form().as_search()
        try:
            context['autocomplete'] = {
                'suburbs': listings.values_list('address_suburb', flat=True).distinct(),
                'postcodes': listings.values_list('address_postcode', flat=True).distinct(),
            }
        except AttributeError:
            # Thrown if listings is an Elasticsearch response
            unique_suburbs_in_order = []
            for i in listings:
                if i.address_suburb not in unique_suburbs_in_order:
                    unique_suburbs_in_order.append(i.address_suburb)

            context['autocomplete'] = {
                'suburbs': unique_suburbs_in_order,
                'postcodes': sorted(list(set([i.address_postcode for i in listings])))
            }

        context['autocomplete']['properties'] = [(i.get_absolute_url(), i.address_display_string()) for i in listings]
        agents = []
        for listing in listings:
            agents += [(i.agent.get_url(), i.agent.title) for i in listing.agents.all()]
        context['autocomplete']['agents'] = agents

        return context


class ListingInspectionSearchView(ListingSearchView):
    form_class = ListingInspectionSearchForm
    template_name = "listings/inspection_search.html"

    def get_listings(self):
        return self.get_form().as_search()

    def get_context_data(self, **kwargs):
        context = super(ListingInspectionSearchView, self).get_context_data(**kwargs)
        listing_paginator = Paginator(self.get_listings(), self.get_per_page())
        context['inspections'] = listing_paginator.get_page(self.get_page_number())
        return context


class ListingAuctionSearchView(ListingSearchView):
    form_class = ListingAuctionSearchForm
    template_name = "listings/auction_search.html"


class ListingDetailView(DetailView, FormMixin):
    model = PropertyListing
    template_name = "listings/listing_detail.html"
    form_class = ListingEnquiryForm

    def get_initial(self):
        return {
            'listing': self.get_object()
        }

    def get_context_data(self, **kwargs):
        context = super(ListingDetailView, self).get_context_data(**kwargs)
        if School and self.get_object().location:
            context['schools'] = School.closest_to_listing(self.get_object())
        return context

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        form.save()
        self.object = self.get_object()
        context = self.get_context_data()
        context['success'] = True
        return self.render_to_response(context)
