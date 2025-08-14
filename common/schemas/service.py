from rest_framework import serializers
from apps.services.models import TypeService

class TypeServiceNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = TypeService
        fields = ['id', 'nome']
