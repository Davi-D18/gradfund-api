from rest_framework.routers import DefaultRouter
from django.urls import path
from apps.payments.controllers.payment_controller import PaymentViewSet
from apps.payments.controllers.webhook_controller import webhook_mercadopago
from apps.payments.controllers.oauth_controller import (
    get_oauth_url, oauth_callback, check_mp_connection, disconnect_mp_account
)

router = DefaultRouter()
router.register('payments', PaymentViewSet)

urlpatterns = [
    path('payments/webhook/', webhook_mercadopago, name='payment-webhook'),
    path('payments/oauth/connect/', get_oauth_url, name='oauth-connect'),
    path('payments/oauth/callback/', oauth_callback, name='oauth-callback'),
    path('payments/oauth/status/', check_mp_connection, name='oauth-status'),
    path('payments/oauth/disconnect/', disconnect_mp_account, name='oauth-disconnect'),
] + router.urls