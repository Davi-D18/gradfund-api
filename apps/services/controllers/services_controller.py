from rest_framework import permissions
from rest_framework.decorators import action
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
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
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
        if self.action == 'list':
            return qs.filter(ativo=True)

        # rota /servicos/meus/: todos (ativos ou não) do usuário logado
        if self.action == 'buscar_servicos_usuario':
            usuario = get_object_or_404(CustomerUser, usuario=self.request.user)
            return qs.filter(estudante=usuario)

        # retrieve, update, partial_update e destroy: todos (ativos ou não) do próprio usuário
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy']:
            usuario = get_object_or_404(CustomerUser, usuario=self.request.user)
            return qs.filter(estudante=usuario)

        # por segurança, não expor nada inesperado
        return qs.none()

    @action(detail=False, methods=['get'], url_path='meus')
    def buscar_servicos_usuario(self, request):
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class TypeServiceViewSet(ModelViewSet):
    queryset = TypeService.objects.all()
    serializer_class = TypeServiceSerializer
    permission_classes = [permissions.AllowAny]
