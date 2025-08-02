from rest_framework import permissions
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from apps.services.schemas.service_schema import ServiceSerializer, TypeServiceSerializer
from apps.services.models.services import Service, TypeService
from apps.authentication.models import CustomerUser


class ServiceViewSet(ModelViewSet):
    queryset = Service.objects.select_related(
        'estudante__usuario',
        'estudante__universidade', 
        'estudante__curso',
        'tipo_servico'
    ).filter(ativo=True)
    serializer_class = ServiceSerializer

    @action(detail=False, methods=['get'], url_path='meus')
    def buscar_servicos_usuario(self, request):
        usuario = get_object_or_404(CustomerUser, usuario=request.user)
        qs = self.get_queryset().filter(estudante=usuario.pk)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class TypeServiceViewSet(ModelViewSet):
    queryset = TypeService.objects.all()
    serializer_class = TypeServiceSerializer
    permission_classes = [permissions.AllowAny]