from rest_framework import serializers
from apps.services.models.services import Service, TypeService
from apps.authentication.models import CustomerUser
from apps.academic.models.academics import Universidade, Curso
from django.contrib.auth.models import User


class CustomerUserNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']


class UniversidadeNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Universidade
        fields = ['nome', 'sigla']


class CursoNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curso
        fields = ['nome']


class TypeServiceNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeService
        fields = ['id', 'nome']


class EstudanteNestedSerializer(serializers.ModelSerializer):
    usuario = CustomerUserNestedSerializer(read_only=True)
    universidade = UniversidadeNestedSerializer(read_only=True)
    curso = CursoNestedSerializer(read_only=True)
    
    class Meta:
        model = CustomerUser
        fields = ['id', 'usuario', 'universidade', 'curso']


class EstudanteDetailSerializer(serializers.ModelSerializer):
    usuario = CustomerUserNestedSerializer(read_only=True)
    universidade = UniversidadeNestedSerializer(read_only=True)
    curso = CursoNestedSerializer(read_only=True)
    
    class Meta:
        model = CustomerUser
        fields = ['id', 'usuario', 'universidade', 'curso']


class ServiceSerializer(serializers.ModelSerializer):
    estudante = EstudanteNestedSerializer(read_only=True)
    tipo_servico = TypeServiceNestedSerializer(read_only=True)
    
    # Campos para escrita (aceita ID)
    estudante_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomerUser.objects.all(),
        source='estudante',
        write_only=True,
        required=True
    )
    
    tipo_servico_id = serializers.PrimaryKeyRelatedField(
        queryset=TypeService.objects.all(),
        source='tipo_servico',
        write_only=True,
        required=True
    )

    class Meta:
        model = Service
        fields = ['id', 'titulo', 'descricao', 'preco', 'criado_em', 'ativo',
                 'estudante', 'tipo_servico', 'estudante_id', 'tipo_servico_id']
    
    def validate_preco(self, preco):
        if preco < 0:
            raise serializers.ValidationError("O preço não pode ser negativo.")
        return preco    
  
    
    def validate(self, data):
        request = self.context['request']
        
        # Acessar o tipo de usuário do JWT token
        if hasattr(request, 'auth') and request.auth:
            token_payload = request.auth.payload
            tipo_usuario = token_payload.get('tipo_usuario')
            
            if tipo_usuario != 'universitario':
                raise serializers.ValidationError({"tipo_usuario": "Apenas universitários podem criar serviços."})
        else:
            raise serializers.ValidationError("Token de autenticação inválido.")
        
        return data

    def validate_estudante_id(self, estudante):
        request = self.context['request']
        
        # Verificar se o estudante informado é o mesmo usuário da requisição
        if hasattr(request, 'user') and request.user.is_authenticated:
            customer_user = request.user.usuario_user
            if estudante != customer_user:
                raise serializers.ValidationError("Você só pode criar serviços para seu próprio perfil.")
        else:
            raise serializers.ValidationError("Usuário não autenticado.")
            
        return estudante


class ServiceDetailSerializer(serializers.ModelSerializer):
    estudante = EstudanteDetailSerializer(read_only=True)
    tipo_servico = TypeServiceNestedSerializer(read_only=True)
    
    class Meta:
        model = Service
        fields = ['id', 'titulo', 'descricao', 'preco', 'criado_em', 'ativo',
                 'estudante', 'tipo_servico']


class TypeServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeService
        fields = '__all__'
