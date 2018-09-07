from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from .forms import ListingSearchForm
from .models import PropertyListing
from .serializers import ListingSerializer


class ListingViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving listings.
    """
    def list(self, request):
        queryset = ListingSearchForm(request.data)
        serializer = ListingSerializer(queryset.as_search(), many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = PropertyListing.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = ListingSerializer(user)
        return Response(serializer.data)
