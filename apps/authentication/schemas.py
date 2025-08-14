from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomerUser
from .constants.user import USER_TYPE_CHOICES
from apps.academic.models.academics import Universidade, Curso
from common.schemas.user import UserNestedSerializer
from common.schemas.academic import UniversidadeNestedSerializer, CursoNestedSerializer


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    # Campos do CustomerUser (usando nomes em vez de IDs)
    tipo_usuario = serializers.ChoiceField(choices=USER_TYPE_CHOICES, required=True, write_only=True, error_messages={'required': 'O tipo de usuário é obrigatório'})
    universidade = serializers.SlugRelatedField(queryset=Universidade.objects.all(), slug_field='nome', required=False, allow_null=True, write_only=True)
    curso = serializers.SlugRelatedField(queryset=Curso.objects.all(), slug_field='nome', required=False, allow_null=True, write_only=True)
    ano_formatura = serializers.IntegerField(required=False, allow_null=True, write_only=True)

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password', 'tipo_usuario', 'universidade', 'curso', 'ano_formatura']
        extra_kwargs = {
            'username': {'required': True, 'error_messages': {'required': 'O nome de usuário é obrigatório'}},
            'email': {'required': True, 'error_messages': {'required': 'O email é obrigatório'}},
        }

    def validate_username(self, value):
        """
        Valida se o nome de usuário já existe no sistema.
        """
        User = get_user_model()
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("O nome de usuário já está em uso")
        
        # Validar formato do username
        if len(value) < 3:
            raise serializers.ValidationError("O nome de usuário deve ter pelo menos 3 caracteres")
        
        return value
    
    def validate_email(self, value):
        """
        Valida se o email já existe e tem formato válido.
        """
        import re
        User = get_user_model()
        
        # Validar formato do email
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, value):
            raise serializers.ValidationError("Formato de email inválido")
        
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("O email já está em uso")
        return value
    
    def validate_ano_formatura(self, value):
        """
        Valida se o ano de formatura é válido.
        """
        if value is not None:
            from datetime import datetime
            current_year = datetime.now().year
            
            if value < current_year:
                raise serializers.ValidationError("O ano de formatura não pode ser no passado")
            if value > current_year + 10:
                raise serializers.ValidationError("O ano de formatura não pode ser mais de 10 anos no futuro")
        
        return value

    def validate_universidade(self, value):
        """
        Verifica se universidade é informada, se for, o campo curso se torna obrigatório
        """
        if value is not None:
            if not self.initial_data.get('curso'):
                raise serializers.ValidationError("Curso é obrigatório quando universidade é informada")

        return value

    def create(self, validated_data):
        # Separar dados do User e CustomerUser
        customer_data = {
            'tipo_usuario': validated_data.pop('tipo_usuario', None),
            'universidade': validated_data.pop('universidade', None),
            'curso': validated_data.pop('curso', None),
            'ano_formatura': validated_data.pop('ano_formatura', None),
        }
        
        # Criar User
        user = get_user_model().objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        
        # Criar CustomerUser (sempre criado pois tipo_usuario é obrigatório)
        CustomerUser.objects.create(usuario=user, **customer_data)
        
        return user


class TokenObtainPairSerializer(TokenObtainPairSerializer):
    credential = serializers.CharField(
        write_only=True,
        error_messages={'required': 'O nome de usuário ou email é obrigatório'}
    )
    password = serializers.CharField(
        write_only=True,
        error_messages={'required': 'A senha é obrigatória'}
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove o campo username do serializer para não ser obrigatório no login
        self.fields.pop('username', None)

    def validate(self, attrs):
        credential = attrs.get('credential')
        password = attrs.get('password')
        user = None

        User = get_user_model()
        if '@' in credential:
            try:
                user = User.objects.get(email=credential)
            except User.DoesNotExist:
                pass
        if user is None:
            try:
                user = User.objects.get(username=credential)
            except User.DoesNotExist:
                pass

        if user and user.check_password(password):
            attrs['username'] = user.username  # Necessário para o SimpleJWT
            return super().validate(attrs)
        else:
            raise serializers.ValidationError({'credential_invalid': 'Nome de usuário/email ou senha inválidos'})

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        
        customer_user = user.usuario_user
        token['tipo_usuario'] = customer_user.tipo_usuario
            
        return token


class CustomerUserProfileSerializer(serializers.ModelSerializer):
    usuario = UserNestedSerializer(read_only=True)
    universidade = UniversidadeNestedSerializer(read_only=True)
    curso = CursoNestedSerializer(read_only=True)
    
    class Meta:
        model = CustomerUser
        fields = ['id', 'usuario', 'tipo_usuario', 'universidade', 'curso', 'ano_formatura']


class CustomerUserUpdateSerializer(serializers.ModelSerializer):
    # Campos do User
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    
    # Campos do CustomerUser
    universidade_id = serializers.PrimaryKeyRelatedField(
        queryset=Universidade.objects.all(),
        source='universidade',
        required=False,
        allow_null=True
    )
    curso_id = serializers.PrimaryKeyRelatedField(
        queryset=Curso.objects.all(),
        source='curso',
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = CustomerUser
        fields = ['username', 'email', 'first_name', 'last_name', 'universidade_id', 'curso_id', 'ano_formatura']
    
    def update(self, instance, validated_data):
        # Separar dados do User e CustomerUser
        user_data = {
            'username': validated_data.pop('username', None),
            'email': validated_data.pop('email', None),
            'first_name': validated_data.pop('first_name', None),
            'last_name': validated_data.pop('last_name', None),
        }
        
        # Atualizar User
        user = instance.usuario
        for field, value in user_data.items():
            if value is not None:
                setattr(user, field, value)
        user.save()
        
        # Atualizar CustomerUser
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        
        return instance
