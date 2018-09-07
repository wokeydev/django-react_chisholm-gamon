"""
General Wagtail CMS Setup.

Includes:
 - Basic Content Page, Content Page w/ Form models (inluding fields form seo_page)
 - Wagtail site settings for Social Media accounts
 - Wagtail site settings for 3rd party API's including Maps, Analytics, Tag manager and Mailchimp or Mandrill
 - A base template including Anayltics/tag manager render and SEO fields
 - A mailbackend to dynamically load the appropriate backend based on 3rd party API settings.
    NOTE: Mail backend needs to be defined as 'cms.email_backend.CMSEmailBackend' in settings.
"""
