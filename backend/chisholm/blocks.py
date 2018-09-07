from wagtail.core import blocks
from wagtail.snippets.blocks import SnippetChooserBlock
from realestate.listings.forms import ListingSearchForm
from realestate.listings import enums as listing_enums
from realestate.listings.serializers import ListingSerializer
from blog.models import BlogPage
from cms.blocks import APIImageChooserBlock, DetailedPageChooserBlock

__all__ = [
    'NewsLetterSignupBlock',
    'WhyChooseUsBlock',
    'TwinPanel'
]


class NewsLetterSignupBlock(blocks.StructBlock):
    title = blocks.CharBlock(default='be the first to know')
    subheading = blocks.CharBlock(required=False)

    class Meta:
        icon = 'fa-newspaper-o'


class WhyChooseUsSectionBase(blocks.StructBlock):
    IMAGE_LOCATION_LEFT = 'l'
    IMAGE_LOCATION_RIGHT = 'r'
    IMAGE_LOCATIONS = [
        (IMAGE_LOCATION_LEFT, 'Left'),
        (IMAGE_LOCATION_RIGHT, 'Right')
    ]

    image = APIImageChooserBlock()
    icon = APIImageChooserBlock()
    image_location = blocks.ChoiceBlock(choices=IMAGE_LOCATIONS, default=IMAGE_LOCATION_LEFT)


class WhyChooseUsOfficesBlock(WhyChooseUsSectionBase):
    offices = DetailedPageChooserBlock(target_model='offices.OfficePage')

    class Meta:
        icon = 'fa-building'


class WhyChooseUsLinksBlock(WhyChooseUsSectionBase):
    links = blocks.ListBlock(DetailedPageChooserBlock(label='Links'))
    image_overlay_text = blocks.CharBlock(required=False)

    class Meta:
        icon = 'fa-link'


class WhyChooseUsBlock(blocks.StructBlock):
    title = blocks.CharBlock(default='why choose us?')
    subheading = blocks.CharBlock(required=False)
    sections = blocks.StreamBlock([
        ('links', WhyChooseUsLinksBlock()),
        ('offices', WhyChooseUsOfficesBlock()),

    ])
    cta_text = blocks.CharBlock(required=False)
    cta_link = DetailedPageChooserBlock(required=False)

    class Meta:
        icon = 'fa-question'


class LatestArticlesPanel(blocks.StructBlock):
    DEFAULT_LENGTH = 3
    number_of_articles = blocks.IntegerBlock(default=DEFAULT_LENGTH)
    see_all_text = blocks.CharBlock(required=False, help_text='Button text for "See all"')
    see_all_link = DetailedPageChooserBlock()

    def get_api_representation(self, value, context=None):
        print(value)
        pages = BlogPage.objects.live().order_by('-date')[:value['number_of_articles']]
        return [i.get_api_representation(context=context) for i in pages]

    class Meta:
        icon = 'fa-rss'


class FastLinkPanel(blocks.StructBlock):
    title = blocks.CharBlock(default='find it fast')
    links = blocks.ListBlock(
        blocks.StructBlock([
            ('page', DetailedPageChooserBlock(required=True)),
            ('tagline', blocks.CharBlock(required=False))
        ])
    )

    class Meta:
        icon = 'fa-bolt'


class ImageLinkBlock(blocks.StructBlock):
    image = APIImageChooserBlock()
    link = DetailedPageChooserBlock()

    class Meta:
        icon = 'fa-picture-o'


class TestimonialsBlock(blocks.StructBlock):
    testimonials = blocks.ListBlock(
        SnippetChooserBlock(target_model='testimonials.Testimonial')
    )

    class Meta:
        icon = 'fa-commenting'


class OurOfficesBlock(blocks.StaticBlock):

    def get_api_representation(self, context=None):
        from offices.models import OfficePage  # noqa - to avoice circle import
        pages = OfficePage.objects.live()
        return [i.get_api_representation(context=context) for i in pages]

    class Meta:
        icon = 'fa-building'


class LatestPropertiesBlock(blocks.StructBlock):
    DEFAULT_LIMIT = 3
    TYPE_SALE = listing_enums.PROPERTY_CLASS_RESIDENTIAL
    TYPE_LEASE = listing_enums.PROPERTY_CLASS_RENTAL
    TYPE_SOLD = 'sold'
    TYPES = [
        (TYPE_SALE, 'Latest Sales'),
        (TYPE_LEASE, 'Latest Rentals'),
        (TYPE_SOLD, 'Latest Sold'),
    ]
    title = blocks.CharBlock(default='Latest Properties')
    property_type = blocks.ChoiceBlock()
    limit = blocks.IntegerBlock(default=DEFAULT_LIMIT)

    def get_api_representation(self, context):
        form_data = {}
        if self.property_type == self.TYPE_SOLD:
            form_data['status'] = listing_enums.STATUS_SOLD
        else:
            form_data['status'] = listing_enums.STATUS_CURRENT
            form_data['property_class'] = self.property_type
        listings = ListingSearchForm(form_data).as_search()[:self.limit]
        return ListingSerializer(listings, many=True).data

    class Meta:
        icon = 'fa-home'


class CallToActionBlock(blocks.StructBlock):
    """
    Block to show a call 2 action with up to 2 buttons
    """
    title = blocks.CharBlock()
    link = DetailedPageChooserBlock()
    secondary_link = DetailedPageChooserBlock(help_text='Will show 2 CTA\'s side by side', required=False)

    class Meta:
        icon = 'fa-exclamation'


class TwinPanel(blocks.StructBlock):
    SPLIT_5050 = '50-50'
    SPLIT_2575 = '25-75'
    SPLIT_7525 = '75-25'
    SPLIT_3366 = '33-66'
    SPLIT_6633 = '66-33'
    SPLITS = [
        (SPLIT_5050, '50% - 50%'),
        (SPLIT_2575, '25% - 75%'),
        (SPLIT_7525, '75% - 25%'),
        (SPLIT_3366, '1/3 - 2/3'),
        (SPLIT_6633, '2/3 - 1/3')
    ]
    split = blocks.ChoiceBlock(choices=SPLITS, default=SPLIT_5050)
    panels = blocks.StreamBlock([
        ('latest_posts', LatestArticlesPanel()),
        ('find_it_fast', FastLinkPanel()),
        ('image_link', ImageLinkBlock()),
        ('testimonials', TestimonialsBlock()),
        ('offices', OurOfficesBlock()),
        ('latest_properties', LatestPropertiesBlock()),
        ('call_to_action', CallToActionBlock())
    ], max_num=2)

    class Meta:
        icon = 'fa-columns'


class SideBar(blocks.StreamBlock):
    SIDEBAR_MAX = 3  # Max number of panels in a sidebar
    panels = blocks.StreamBlock([
        ('latest_posts', LatestArticlesPanel()),
        ('find_it_fast', FastLinkPanel()),
        ('image_link', ImageLinkBlock()),
        ('testimonials', TestimonialsBlock()),
        ('offices', OurOfficesBlock()),
        ('latest_properties', LatestPropertiesBlock()),
        ('call_to_action', CallToActionBlock())
    ], max_num=SIDEBAR_MAX)
