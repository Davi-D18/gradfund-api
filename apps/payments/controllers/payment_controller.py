from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.db.models import Q
from apps.payments.models import Payment
from apps.payments.schemas.payment_schema import (
    PaymentCreateSerializer, 
    PaymentDetailSerializer, 
    PaymentListSerializer
)
from apps.payments.permissions.payment_permissions import (
    CanCreatePayment, 
    IsPaymentParticipant
)
from apps.payments.services.payment_service import PaymentService


class PaymentViewSet(ModelViewSet):
    queryset = Payment.objects.all()
    permission_classes = [CanCreatePayment, IsPaymentParticipant]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        elif self.action == 'list':
            return PaymentListSerializer
        return PaymentDetailSerializer
    
    def get_queryset(self):
        user_profile = self.request.user.usuario_user
        return Payment.objects.filter(
            Q(contratante=user_profile) | Q(prestador=user_profile)
        ).select_related('contratante__usuario', 'prestador__usuario', 'servico')
    
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            payment_service = PaymentService()
            result = payment_service.criar_pagamento(
                contratante=request.user.usuario_user,
                servico_id=serializer.validated_data['servico_id']
            )
            return Response(result, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': 'Erro interno do servidor'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def meus_pagamentos(self, request):
        """Lista pagamentos onde o usuário é contratante"""
        user_profile = request.user.usuario_user
        payments = Payment.objects.filter(contratante=user_profile).select_related(
            'prestador__usuario', 'servico'
        )
        serializer = PaymentListSerializer(payments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def meus_recebimentos(self, request):
        """Lista pagamentos onde o usuário é prestador"""
        user_profile = request.user.usuario_user
        payments = Payment.objects.filter(prestador=user_profile).select_related(
            'contratante__usuario', 'servico'
        )
        serializer = PaymentListSerializer(payments, many=True)
        return Response(serializer.data)