from rest_framework import viewsets
from cms.api_permissions import AlertPermissions
from cms.authentication import AlwaysCSRFSessionAuthentication
from ..models import PropertyAlert
from .serializers import PropertyAlertSerializer


class PropertyAlertViewset(viewsets.ModelViewSet):
    queryset = PropertyAlert.objects.all()
    serializer_class = PropertyAlertSerializer
    permission_classes = [AlertPermissions]
    authentication_classes = [AlwaysCSRFSessionAuthentication]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        if user.is_staff or user.is_superuser:
            return qs
        return qs.filter(email=user.email_address)
