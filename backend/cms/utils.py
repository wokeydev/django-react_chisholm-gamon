import requests
from io import BytesIO
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from wagtail.images.models import Image


def send_email_template(subject, from_email, recipients, template, context, include_cc=True):

    html_content = render_to_string(template, context)
    text_content = strip_tags(html_content)

    try:
        cc = settings.EMAIL_CC
    except AttributeError:  # Not set, pass
        cc = None

    try:
        bcc = settings.EMAIL_BCC
    except AttributeError:  # Not set, pass
        bcc = None

    if not include_cc:  # Allow bypass so not everything get's CC'd
        cc = None
        bcc = None

    if settings.DEBUG and getattr(settings, 'MAIL_RECIPIENT_OVERRIDE'):
        recipients = settings.MAIL_RECIPIENT_OVERRIDE

    if recipients:
        msg = EmailMultiAlternatives(subject, text_content, from_email, recipients, cc=[cc], bcc=[bcc])
        msg.attach_alternative(html_content, "text/html")
        msg.send()


def wagtail_image_from_url(url):
    """
    Accepts a URL to an image and attempts to download and save
    the image as a wagtail.images.Image instance.

    Returns either the new object or None on failure. Will raise exceptions
    on bad http status (as per requests.raise_for_status)
    """

    resp = requests.get(url)
    resp.raise_for_status()

    i = BytesIO(resp.content)
    file_name = url.split('/')[-1]
    cms_image = Image(title=file_name)
    try:
        cms_image.file.save(file_name, i)
        cms_image.save()
        return cms_image
    except Exception as e:
        print(e)
        return None
