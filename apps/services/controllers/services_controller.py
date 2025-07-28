from rest_framework.viewsets import ModelViewSet
from apps.services.schemas.service_schema import ServiceSerializer, TypeServiceSerializer
from apps.services.models.services import Service, TypeService


class ServiceViewSet(ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer


class TypeServiceViewSet(ModelViewSet):
    queryset = TypeService.objects.all()
    serializer_class = TypeServiceSerializer

