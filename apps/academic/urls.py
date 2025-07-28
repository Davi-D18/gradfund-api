from django.urls import path, include


urlpatterns = [
    path('', include('apps.academic.routes.academics_routes')),
]
