from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from apps.services.schemas.service_schema import ServiceSerializer, TypeServiceSerializer
from apps.services.models.services import Service, TypeService
from apps.authentication.models import CustomerUser
from apps.services.permissions import IsOwner


class ServiceViewSet(ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    def get_permissions(self):
        # nas ações retrieve/update/partial_update/destroy, aplica também IsOwner
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOwner()]
        return super().get_permissions()

    def get_queryset(self):
        qs = Service.objects.select_related(
            'estudante__usuario',
            'estudante__universidade',
            'estudante__curso',
            'tipo_servico',
        )

        # rota padrão de listagem: só os ativos, de qualquer usuário
        if self.action =='list':
            return qs.filter(ativo=True)

        return qs

    
    def retrieve(self, request, *args, **kwargs):
        service = self.get_object()

        if not service.ativo:
            user_cust = get_object_or_404(CustomerUser, usuario=request.user)
            if user_cust.tipo_usuario == 'publico_externo':
                raise PermissionDenied({
                    'permission': 'Você não tem permissão para ver esse serviço'
                })

        return super().retrieve(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='meus')
    def buscar_servicos_usuario(self, request):
        qs = Service.objects.select_related(
            'estudante__usuario',
            'estudante__universidade',
            'estudante__curso',
            'tipo_servico'
        ).filter(estudante=get_object_or_404(CustomerUser, usuario=request.user))
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class TypeServiceViewSet(ModelViewSet):
    queryset = TypeService.objects.all()
    serializer_class = TypeServiceSerializer
    permission_classes = [permissions.AllowAny]
