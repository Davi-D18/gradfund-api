from django.urls import path, include

urlpatterns = [
    path('', include('apps.payments.routes.payment_routes')),
]