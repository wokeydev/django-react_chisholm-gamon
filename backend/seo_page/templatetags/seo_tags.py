from django import template

register = template.Library()


@register.inclusion_tag('seo_page/seo_fields.html')
def seo_fields(page):
    return {'page': page}
