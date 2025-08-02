from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.services.controllers.services_controller import ServiceViewSet, TypeServiceViewSet

router = DefaultRouter()
router.register('servicos', ServiceViewSet)
router.register('tipos-servicos', TypeServiceViewSet)

urlpatterns = [
    path('', include(router.urls))
]