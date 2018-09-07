from wagtail.admin.forms import WagtailAdminPageForm
from django.template.defaultfilters import slugify


class NameFieldToSlugForm(WagtailAdminPageForm):
    def full_clean(self):
        self.data = self.data.copy()
        if not self.data.get('slug') and self.data.get('name'):
            self.data['slug'] = slugify(self.data['name'])
        return super(NameFieldToSlugForm, self).full_clean()
