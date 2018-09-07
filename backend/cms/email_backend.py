from django.conf import settings
from django.utils.module_loading import import_string
from anymail.backends import mailgun, mandrill
from wagtail.core.models import Site
from .models import ThirdPartyApiSettings


def get_backend(site=None, fail_silently=True, **kwargs):
    """
    Given a single site configured, or a passed in site, will check the site settings
    for an appropriate API key to set the backend.
    """
    if not site and Site.objects.all().count() == 1:
        site = Site.objects.all().latest('pk')
    if not site:
        return
    mail_class = None

    try:
        api_settings = ThirdPartyApiSettings.for_site(site)
        if api_settings.mandrill:
            settings.ANYMAIL['MANDRILL_API_KEY'] = api_settings.mandrill
            mail_class = mandrill.EmailBackend
        elif api_settings.mailgun:
            settings.ANYMAIL['MAILGUN_API_KEY'] = api_settings.mailgun
            mail_class = mailgun.EmailBackend
    except Exception:
        pass

    if not mail_class:
        mail_class = import_string(settings.FAILOVER_EMAIL_BACKEND)
    return mail_class(fail_silently=fail_silently, **kwargs)


CMSEmailBackend = lambda *args, **kwargs: get_backend(*args, **kwargs)  # noqa
