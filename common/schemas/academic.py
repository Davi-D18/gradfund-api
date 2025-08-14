from rest_framework import serializers
from apps.academic.models.academics import Universidade, Curso

class UniversidadeNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Universidade
        fields = ['id', 'nome', 'sigla']

class CursoNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curso
        fields = ['id', 'nome']