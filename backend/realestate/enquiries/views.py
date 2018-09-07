from django.apps import apps
from rest_framework import exceptions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from cms.authentication import AlwaysCSRFSessionAuthentication
from .serializers import ListingEnquirySerializer


class CreateListingEnquiryApi(APIView):
    """
    Create a Listing Enquiry and store details
    """
    authentication_classes = (AlwaysCSRFSessionAuthentication,)

    def post(self, request, format=None):
        # Add in the current user
        data = request.data.copy()
        if request.user.is_authenticated:
            data.sent_by_user = request.user
        serialized = ListingEnquirySerializer(data=data)
        if serialized.is_valid():
            serialized.save()
            return Response("OK")
        else:
            return Response(serialized.errors)


class CreatePageEnquiryAPI(APIView):
    """
    Create an enquiry for a given EnquiryFormPage child class.

    *Required fields*
    type: the dot.notation app.Model label for the page type
    id: ID / Primary Key of the Page object
    data: array/dictionary of the form fields.

    NOTE: Requires a valid CSRF token, which can be grabbed from the HTTP_X_CSRFTOKEN header
    """
    authentication_classes = (AlwaysCSRFSessionAuthentication,)

    def post(self, request, format=None):
        # Add in the current user
        request_data = request.data.copy()
        form_data = request_data.get('data')
        if request.user.is_authenticated:
            form_data['sent_by_user'] = request.user

        app_name, model_name = request_data.get('type').split('.')
        try:
            page_class = apps.get_model(app_name, model_name)
            obj = page_class.objects.get(pk=request_data.get('id'))
        except Exception as e:
            raise exceptions.NotAcceptable(e)

        form = obj.get_form_class(form_data)
        if form.is_valid():
            obj.process_form_submission(form)
            return Response("OK")
        return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
