from rest_framework import serializers
from apps.payments.models import Payment
from apps.services.models import Service


class PaymentCreateSerializer(serializers.Serializer):
    servico_id = serializers.UUIDField()
    
    def validate_servico_id(self, value):
        try:
            servico = Service.objects.get(id=value, ativo=True)
        except Service.DoesNotExist:
            raise serializers.ValidationError("Serviço não encontrado ou inativo")
        return value


class PaymentDetailSerializer(serializers.ModelSerializer):
    contratante_nome = serializers.CharField(source='contratante.usuario.username', read_only=True)
    prestador_nome = serializers.CharField(source='prestador.usuario.username', read_only=True)
    servico_titulo = serializers.CharField(source='servico.titulo', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'contratante_nome', 'prestador_nome', 'servico_titulo',
            'valor_total', 'status', 'metodo_pagamento', 'data_criacao',
            'data_atualizacao', 'data_aprovacao', 'observacoes'
        ]
        read_only_fields = ['id', 'data_criacao', 'data_atualizacao']


class PaymentListSerializer(serializers.ModelSerializer):
    servico_titulo = serializers.CharField(source='servico.titulo', read_only=True)
    contratante_nome = serializers.CharField(source='contratante.usuario.username', read_only=True)
    prestador_nome = serializers.CharField(source='prestador.usuario.username', read_only=True)
    
    class Meta:
        model = Payment
        fields = [
            'id', 'servico_titulo', 'contratante_nome', 'prestador_nome',
            'valor_total', 'status', 'data_criacao'
        ]