from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.academic.controllers.academics_controller import UniversidadeViewSet, CursoViewSet

router = DefaultRouter()
router.register('universidades', UniversidadeViewSet)
router.register('cursos', CursoViewSet)

urlpatterns = [
    path('', include(router.urls))
]