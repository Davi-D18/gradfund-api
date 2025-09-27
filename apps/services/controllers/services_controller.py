from rest_framework import permissions
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from apps.services.schemas.service_schema import (
    ServiceSerializer,
    ServiceDetailSerializer,
    TypeServiceSerializer,
)
from apps.services.models.services import Service, TypeService
from apps.authentication.models import CustomerUser
from apps.services.permissions import IsServiceOwner, CanViewInactiveService


class ServiceViewSet(ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [CanViewInactiveService]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ServiceDetailSerializer
        return ServiceSerializer

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [permissions.IsAuthenticated(), IsServiceOwner()]
        return [perm() for perm in self.permission_classes]

    def get_queryset(self):
        qs = Service.objects.select_related(
            "estudante__usuario",
            "estudante__universidade",
            "estudante__curso",
            "tipo_servico",
        )

        if self.action == "list":
            return qs.filter(ativo=True)
        return qs

    @action(detail=False, methods=["get"], url_path="meus")
    def buscar_servicos_usuario(self, request):
        estudante = get_object_or_404(CustomerUser, usuario=request.user)
        qs = Service.objects.select_related(
            "estudante__usuario",
            "estudante__universidade",
            "estudante__curso",
            "tipo_servico",
        ).filter(estudante=estudante)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class TypeServiceViewSet(ModelViewSet):
    queryset = TypeService.objects.all()
    serializer_class = TypeServiceSerializer
    permission_classes = [permissions.AllowAny]
