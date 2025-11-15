from rest_framework.routers import DefaultRouter
from django.urls import path
from apps.payments.controllers.payment_controller import PaymentViewSet
from apps.payments.controllers.webhook_controller import webhook_mercadopago


router = DefaultRouter()
router.register('payments', PaymentViewSet)

urlpatterns = [
    path('payments/webhook/', webhook_mercadopago, name='payment-webhook'),
] + router.urls
