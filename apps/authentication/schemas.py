from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomerUser
from .constants.user import USER_TYPE_CHOICES
from apps.academic.models.academics import Universidade, Curso


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    # Campos do CustomerUser
    tipo_usuario = serializers.ChoiceField(choices=USER_TYPE_CHOICES, required=True, write_only=True, error_messages={'required': 'O tipo de usuário é obrigatório'})
    universidade = serializers.PrimaryKeyRelatedField(queryset=Universidade.objects.all(), required=False, allow_null=True, write_only=True)
    curso = serializers.PrimaryKeyRelatedField(queryset=Curso.objects.all(), required=False, allow_null=True, write_only=True)
    ano_formatura = serializers.IntegerField(required=False, allow_null=True, write_only=True)

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password', 'tipo_usuario', 'universidade', 'curso', 'ano_formatura']
        extra_kwargs = {
            'username': {'required': True, 'error_messages': {'required': 'O nome de usuário é obrigatório'}},
            'email': {'required': True, 'error_messages': {'required': 'O email é obrigatório'}},
        }

    def validate_email(self, value):
        """
        Valida se o email já existe no sistema.
        """
        User = get_user_model()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("O email já está em uso")
        return value

    def validate_username(self, value):
        """
        Valida se o nome de usuário já existe no sistema.
        """
        User = get_user_model()
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("O nome de usuário já está em uso")
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
        return token