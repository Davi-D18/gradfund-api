from django.urls import path, include
from .controllers.websocket_controller import websocket_status, clear_websocket_connections
from .controllers.debug_controller import debug_current_user, debug_all_users
from .controllers.token_debug_controller import debug_token, debug_current_user_api
from .controllers.test_auth_controller import test_auth_endpoint, test_public_endpoint
from .controllers.test_notification_controller import test_notification
from .controllers.test_controller import test_chat_notification

urlpatterns = [
    path('', include('apps.chat.routes.chat_routes')),
    path('websocket/status/', websocket_status, name='websocket-status'),
    path('websocket/clear/', clear_websocket_connections, name='websocket-clear'),
    path('debug/current-user/', debug_current_user, name='debug-current-user'),
    path('debug/all-users/', debug_all_users, name='debug-all-users'),
    path('debug/token/', debug_token, name='debug-token'),
    path('debug/api-user/', debug_current_user_api, name='debug-api-user'),
    path('test/auth/', test_auth_endpoint, name='test-auth'),
    path('test/public/', test_public_endpoint, name='test-public'),
    path('test/notification/', test_notification, name='test-notification'),
    path('test/chat-notification/', test_chat_notification, name='test-chat-notification'),
]