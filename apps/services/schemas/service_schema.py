from rest_framework import serializers
from apps.services.models.services import Service, TypeService
from apps.authentication.models import CustomerUser


class ServiceSerializer(serializers.ModelSerializer):
    estudante = serializers.SlugRelatedField(
        queryset=CustomerUser.objects.all(),
        slug_field='usuario__username',
        required=False
    )
    
    tipo_servico = serializers.SlugRelatedField(
        queryset=TypeService.objects.all(),
        slug_field='nome',
        required=True
    )

    class Meta:
        model = Service
        fields = ['id', 'titulo', 'descricao', 'preco', 'criado_em', 'atualizado_em', 'ativo',
                 'estudante', 'tipo_servico']


    def validate_preco(self, preco):
        if preco < 0:
            raise serializers.ValidationError("O preço não pode ser negativo.")
        return preco    
  
    
    # Verifica se o usuário que está criando o serviço é um estudante universitário
    def validate(self, data):
        request = self.context['request']
        
        # Acessar o tipo de usuário do JWT token
        if hasattr(request, 'auth') and request.auth:
            token_payload = request.auth.payload
            tipo_usuario = token_payload.get('tipo_usuario')
            
            if tipo_usuario != 'universitario':
                raise serializers.ValidationError({"tipo_usuario": "Apenas estudantes universitários podem criar serviços."})
        else:
            raise serializers.ValidationError("Token de autenticação inválido.")
        
        # Definir estudante automaticamente como o usuário logado se não informado
        if not data.get('estudante'):
            data['estudante'] = request.user.usuario_user
            
        return data

    def validate_estudante(self, estudante):
        request = self.context['request']
        
        # Verificar se o estudante informado é o mesmo usuário da requisição
        if hasattr(request, 'user') and request.user.is_authenticated:
            customer_user = request.user.usuario_user
            if estudante != customer_user:
                raise serializers.ValidationError("Você só pode criar serviços para seu próprio perfil.")
        else:
            raise serializers.ValidationError("Usuário não autenticado.")
            
        return estudante


class TypeServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeService
        fields = '__all__'
