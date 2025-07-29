from rest_framework import serializers
from apps.academic.models.academics import Universidade, Curso
from utils.formatters import StringFormatter


class UniversidadeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Universidade
        fields = ['id', 'nome', 'sigla', 'cidade', 'estado']
    
    def validate_nome(self, value):
        value = StringFormatter.format_text(value, 'title')
        if len(value) < 3:
            raise serializers.ValidationError("Nome da universidade deve ter pelo menos 3 caracteres")
        return value
    
    def validate_sigla(self, value):
        value = StringFormatter.format_text(value, 'upper')
        if value and len(value) > 20:
            raise serializers.ValidationError("Sigla não pode ter mais de 20 caracteres")
        return value
    
    def validate_cidade(self, value):
        return StringFormatter.format_text(value, 'title')
    
    def validate_estado(self, value):
        return StringFormatter.format_text(value, 'title')


class CursoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curso
        fields = "__all__"
    
    
    def validate_nome(self, value):
        value = StringFormatter.format_text(value, 'title')
        if len(value) < 3:
            raise serializers.ValidationError("Nome do curso deve ter pelo menos 3 caracteres")
        return value