from django.db import models

from modelcluster.fields import ParentalKey
from wagtail.search import index
from wagtail.core.models import Page, Orderable
from wagtail.snippets.models import register_snippet
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.api.fields import ImageRenditionField
from wagtail.admin.edit_handlers import (RichTextField, FieldPanel,
                                         InlinePanel, TabbedInterface, ObjectList)
from wagtail.api import APIField
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.template import loader

from seo_page.models import SEOFields
from ..enquiries.models import EnquiryFormPage
from ..enquiries.forms import PageEnquiryForm
from ..listings import enums as listing_enums
from .settings import AGENTS_PER_PAGE
from . import enums


class AgentBase(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    source_id = models.CharField(max_length=50, blank=True, default="")
    name_short = models.CharField(max_length=50, blank=True, default="",
                                  help_text="Short version of the agent name, a nickname or first name.")
    job_title = models.CharField(max_length=255, blank=True)
    video_url = models.URLField(blank=True, default="")
    email = models.EmailField(blank=True, default="")
    phone = models.CharField(max_length=25, blank=True, default="")
    office_phone = models.CharField(max_length=25, blank=True, default="")

    class Meta:
        abstract = True


class AgentPage(SEOFields, EnquiryFormPage, AgentBase):
    about_me = RichTextField(blank=True, default="")
    profile_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    landscape_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = Page.content_panels + [
        FieldPanel('name_short'),
        FieldPanel('job_title'),
        FieldPanel('email'),
        FieldPanel('phone'),
        FieldPanel('about_me'),
        FieldPanel('video_url'),
        ImageChooserPanel('profile_image'),
        ImageChooserPanel('landscape_image'),
        InlinePanel('offices', label="Offices"),
        InlinePanel('categories', label="Categories/Labels"),
        InlinePanel('specialty_suburbs', label="Specialty suburbs"),
        InlinePanel('team_members', label="Team Members"),
        InlinePanel('gallery', label="Image Gallery")
    ]

    settings_panels = Page.settings_panels + [
        FieldPanel('source_id')
    ]

    search_fields = Page.search_fields + [
        index.SearchField('name_short', partial_match=True)
    ]
    email_template = "email/agent_enquiry.html"

    api_fields = [
        APIField('slug'),
        APIField('pk'),
        APIField('title'),
        APIField('name_short'),
        APIField('job_title'),
        APIField('video_url'),
        APIField('email'),
        APIField('phone'),
        APIField('office_phone'),
        APIField('about_me'),
        APIField('profile_image'),
        APIField('landscape_image'),
        APIField('profile_image_thumbnail', serializer=ImageRenditionField(
            enums.PROFILE_IMAGE_THUMBNAIL,
            source=profile_image
        )),
        APIField('offices'),
        APIField('team_members'),
        APIField('gallery')
    ]

    @property
    def all_testimonials(self):
        from ..testimonials.models import Testimonial
        return Testimonial.objects.filter(agents__agent=self)

    def get_listings(self):
        # return PropertyListing.objects.filter(agents__office=self)
        return self.listing_agent.all()

    @property
    def latest_listings_forsale(self):
        return self.get_listings().filter(
            listing__status=listing_enums.STATUS_CURRENT,
            listing__listing_type=listing_enums.LISTING_TYPE_SALE
        ).order_by('-listing__created')

    @property
    def latest_listings_forrent(self):
        return self.get_listings().filter(
            listing__status=listing_enums.STATUS_CURRENT,
            listing__listing_type=listing_enums.LISTING_TYPE_LEASE
        ).order_by('-listing__created')

    @property
    def latest_listings_sold(self):
        return self.get_listings().filter(
            listing__status=listing_enums.STATUS_SOLD
        ).order_by('-listing__created')

    def get_recipients(self):
        recipients = super().get_recipients()
        recipients.append(self.email)
        return recipients


AgentPage.edit_handler = TabbedInterface([
    ObjectList(AgentPage.content_panels, heading='Content'),
    ObjectList(AgentPage.promote_panels, heading='Promote'),
    ObjectList(AgentPage.settings_panels, heading='Settings', classname="settings"),
    ObjectList(AgentPage.seo_panels, heading='SEO'),
])


@register_snippet
class AgentCategory(models.Model):
    category_name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.category_name

    def __str__(self):
        return self.__unicode__()


class AgentPageCategoryChoice(Orderable):
    page = ParentalKey('agents.AgentPage', related_name='categories')
    category = models.ForeignKey('agents.AgentCategory', on_delete=models.CASCADE)

    panels = [
        SnippetChooserPanel('category')
    ]


class AgentPageOffice(Orderable):
    """An office this agent works for."""
    offices = ParentalKey('agents.AgentPage', related_name='offices')
    office = models.ForeignKey('offices.OfficePage', on_delete=models.CASCADE)


class AgentPageSuburbs(Orderable):
    """Spacialty Suburbs for this agent"""
    page = ParentalKey('agents.AgentPage', related_name='specialty_suburbs')
    suburb = models.CharField(max_length=255)


class AgentPageTeamMembers(Orderable):
    """Other agents who create a "team" with this agent."""
    team_members = ParentalKey('agents.AgentPage', related_name='team_members')
    agent = models.ForeignKey('agents.AgentPage', related_name="+", on_delete=models.CASCADE)


class AgentPageGalleryItem(Orderable):
    page = ParentalKey('agents.AgentPage', related_name='gallery')
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    panels = [
        ImageChooserPanel('image')
    ]


class AgentIndexPage(SEOFields, Page):
    subpage_types = ['agents.AgentPage']
    contact_form = PageEnquiryForm()

    @property
    def agents(self):
        return AgentPage.objects.live().descendant_of(self)

    def serve(self, request, *args, **kwargs):
        if request.is_ajax() or request.GET.get('is_ajax'):
            return self.as_json(request)
        return super(AgentIndexPage, self).serve(request, *args, **kwargs)

    def get_per_page_kwarg(self):
        return 'per_page'

    def get_page_kwarg(self):
        return 'page'

    def get_form_class(self):
        # As Wagtail mixed models and views we get circular imports
        from .forms import AgentSearchForm
        return AgentSearchForm

    def get_context(self, request, *args, **kwargs):
        context = super(AgentIndexPage, self).get_context(request, *args, **kwargs)

        context['form'] = self.get_form_class()(request.GET)
        context['paginator'] = Paginator(
            context['form'].as_search(self.agents),
            request.GET.get(self.get_per_page_kwarg(), AGENTS_PER_PAGE)
        )
        page_num = request.GET.get(self.get_page_kwarg(), 1)
        try:
            context['page'] = context['paginator'].page(page_num)
        except Exception:
            context['page'] = context['paginator'].page(1)
        return context

    def as_json(self, request):
        from .serializers import AgentPageSerializer  # noqa
        form = self.get_form_class()(request.GET)
        paginator = Paginator(
            form.as_search(self.agents),
            request.GET.get(self.get_per_page_kwarg(), AGENTS_PER_PAGE)
        )
        page_num = request.GET.get(self.get_page_kwarg(), 1)
        try:
            page = paginator.page(page_num)
        except Exception:
            page = paginator.page(1)

        t = loader.get_template('agents/include/agent_list_item.html')
        rendered_agents = ''.join(
            [t.render({'agent': x}, request) for x in page.object_list]
        )
        context = {
            'meta': {
                'page': page.number,
                'total_pages': page.paginator.num_pages,
                'total_results': page.paginator.count
            },
            # 'agents': AgentPageSerializer(page.object_list, many=True).data,
            'rendered_agents': rendered_agents,
        }
        return JsonResponse(context)


AgentIndexPage.edit_handler = TabbedInterface([
    ObjectList(AgentIndexPage.content_panels, heading='Content'),
    ObjectList(AgentIndexPage.promote_panels, heading='Promote'),
    ObjectList(AgentIndexPage.settings_panels, heading='Settings', classname="settings"),
    ObjectList(AgentIndexPage.seo_panels, heading='SEO'),
])
