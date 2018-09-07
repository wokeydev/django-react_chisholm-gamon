"""chisholn URL Configuration

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
from django.contrib import admin
from django.conf.urls import url, include
from django.urls import path
from django.conf import settings
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.core import urls as wagtail_urls
from wagtail.contrib.sitemaps import views
from wagtail.contrib.sitemaps.sitemap_generator import Sitemap
from cms import urls as cms_urls
from realestate.listings import urls as listing_urls
from realestate.listings.sitemap import PropertySitemap
from realestate.testimonials import urls as testimonial_urls
from realestate.enquiries import urls as enq_urls
from realestate import urls as re_urls
from blog import urls as blog_urls
from django.conf.urls.static import static


sitemaps = {
    'properties': PropertySitemap,
    'website': Sitemap
}

urlpatterns = [
    url('admin/', admin.site.urls),
    url(r'^cms/', include(wagtailadmin_urls)),
    url(r'^documents/', include(wagtaildocs_urls)),
    url(r'^pages/', include(wagtail_urls)),
    url(r'^blog/', include(blog_urls, namespace="blog")),
    url(r'^testimonials/', include(testimonial_urls)),
    url(r'^properties/', include(listing_urls)),
    url(r'^enquiries/', include(enq_urls)),
    path('sitemap.xml', views.index, {'sitemaps': sitemaps}),
    path('sitemap-<section>.xml', views.sitemap, {'sitemaps': sitemaps},
         name="django.contrib.sitemaps.views.sitemap"),
    url(r'', include(cms_urls)),
    url(r'', include(wagtail_urls)),
    url(r'^api/', include(re_urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
