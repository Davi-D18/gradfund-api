from rest_framework.viewsets import ModelViewSet
from apps.academic.schemas.academic_schema import CursoSerializer, UniversidadeSerializer
from apps.academic.models.academics import Curso, Universidade


class UniversidadeViewSet(ModelViewSet):
    queryset = Universidade.objects.all()
    serializer_class = UniversidadeSerializer


class CursoViewSet(ModelViewSet):
    queryset = Curso.objects.all()
    serializer_class = CursoSerializer
