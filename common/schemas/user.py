from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.authentication.models import CustomerUser

User = get_user_model()

class UserNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']

class UserCompactSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']

class CustomerUserNestedSerializer(serializers.ModelSerializer):
    usuario = UserNestedSerializer(read_only=True)
    class Meta:
        model = CustomerUser
        fields = ['id', 'usuario', 'tipo_usuario']