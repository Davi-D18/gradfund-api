from django.urls import path, include


urlpatterns = [
    path('', include('apps.services.routes.services_routes')),
]
