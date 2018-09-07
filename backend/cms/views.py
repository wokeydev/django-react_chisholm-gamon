from __future__ import absolute_import, unicode_literals
import csv
import datetime
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils.encoding import smart_str
from django.core.exceptions import PermissionDenied
from wagtail.utils.pagination import paginate
from wagtail.core.models import Page, UserPagePermissionsProxy, get_page_models
from wagtail.contrib.forms.models import AbstractForm
from wagtail.contrib.forms.forms import SelectDateForm
from wagtail.core import hooks
from django.contrib.contenttypes.models import ContentType
from .models import AbstractFixedFormPage
from .models import RobotsTxtSettings
_FORM_CONTENT_TYPES = None


def robots_txt(request):
    try:
        robots_obj = RobotsTxtSettings.for_site(request.site)
        robots_txt = robots_obj.robots_txt
    except RobotsTxtSettings.DoesNotExist:
        robots_txt = ""
    return HttpResponse(robots_txt, content_type="text/plain")


def get_form_types():
    global _FORM_CONTENT_TYPES
    if _FORM_CONTENT_TYPES is None:
        form_models = [
            model for model in get_page_models()
            if issubclass(model, AbstractForm) or issubclass(model, AbstractFixedFormPage)
        ]

        _FORM_CONTENT_TYPES = list(
            ContentType.objects.get_for_models(*form_models).values()
        )
    return _FORM_CONTENT_TYPES


def get_forms_for_user(user):
    """
    Return a queryset of form pages that this user is allowed to access the submissions for
    """
    editable_forms = UserPagePermissionsProxy(user).editable_pages()
    editable_forms = editable_forms.filter(content_type__in=get_form_types())

    # Apply hooks
    for fn in hooks.get_hooks('filter_form_submissions_for_user'):
        editable_forms = fn(user, editable_forms)

    return editable_forms


def forms_index(request):
    # We are overriding Wagtail forms CMS models to force Forms into the menu with our custom form submisison pages
    print("MY FORM INDEX")
    form_pages = get_forms_for_user(request.user)

    paginator, form_pages = paginate(request, form_pages)

    return render(request, 'wagtailforms/index.html', {
        'form_pages': form_pages,
    })


def list_submissions(request, page_id):
    if not get_forms_for_user(request.user).filter(id=page_id).exists():
        raise PermissionDenied

    form_page = get_object_or_404(Page, id=page_id).specific
    form_submission_class = form_page.get_submission_class()

    data_fields = form_page.get_data_fields()

    submissions = form_submission_class.objects.filter(page=form_page).order_by('submit_time')
    data_headings = [label for name, label in data_fields]

    select_date_form = SelectDateForm(request.GET)
    if select_date_form.is_valid():
        date_from = select_date_form.cleaned_data.get('date_from')
        date_to = select_date_form.cleaned_data.get('date_to')
        # careful: date_to should be increased by 1 day since the submit_time
        # is a time so it will always be greater
        if date_to:
            date_to += datetime.timedelta(days=1)
        if date_from and date_to:
            submissions = submissions.filter(submit_time__range=[date_from, date_to])
        elif date_from and not date_to:
            submissions = submissions.filter(submit_time__gte=date_from)
        elif not date_from and date_to:
            submissions = submissions.filter(submit_time__lte=date_to)

    if request.GET.get('action') == 'CSV':
        # return a CSV instead
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment;filename=export.csv'

        # Prevents UnicodeEncodeError for labels with non-ansi symbols
        data_headings = [smart_str(label) for label in data_headings]

        writer = csv.writer(response)
        writer.writerow(data_headings)
        for s in submissions:
            data_row = []
            form_data = s.get_data()
            for name, label in data_fields:
                val = form_data.get(name)
                if isinstance(val, list):
                    val = ', '.join(val)
                data_row.append(smart_str(val))
            writer.writerow(data_row)
        return response

    paginator, submissions = paginate(request, submissions)

    data_rows = []
    for s in submissions:
        form_data = s.get_data()
        data_row = []
        for name, label in data_fields:
            val = form_data.get(name)
            if isinstance(val, list):
                val = ', '.join(val)
            data_row.append(val)
        data_rows.append({
            "model_id": s.id,
            "fields": data_row
        })

    return render(request, 'wagtailforms/index_submissions.html', {
        'form_page': form_page,
        'select_date_form': select_date_form,
        'submissions': submissions,
        'data_headings': data_headings,
        'data_rows': data_rows
    })
