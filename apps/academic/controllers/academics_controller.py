from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet
from apps.academic.schemas.academic_schema import CursoSerializer, UniversidadeSerializer
from apps.academic.models.academics import Curso, Universidade


class UniversidadeViewSet(ModelViewSet):
    queryset = Universidade.objects.all()
    serializer_class = UniversidadeSerializer
    permission_classes = [permissions.AllowAny]


class CursoViewSet(ModelViewSet):
    queryset = Curso.objects.all()
    serializer_class = CursoSerializer
    permission_classes = [permissions.AllowAny]
