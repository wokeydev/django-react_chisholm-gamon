# urls.py
from django.conf import settings
from .api import api_router
from .views import robots_txt, forms_index, list_submissions
from django.conf.urls import url
from rest_framework.documentation import include_docs_urls

urlpatterns = [
    url(r'^robots\.txt$', robots_txt),
    url(r'api/cms/', api_router.urls),
    url(r'cms/forms/$', forms_index),
    url(r'^cms/forms/submissions/(\d+)/$', list_submissions, name='list_submissions'),
]


# On dev environments we want the API docs browsable
if settings.DEBUG:
    urlpatterns.append(
        url(r'api/docs/', include_docs_urls(title='Chisholm & Gamon API Docs')),
    )

"""
With this configuration, pages will be available at /api/cms/pages/,
images at /api/cms/images/ and documents at /api/cms/documents/
"""
