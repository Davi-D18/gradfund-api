from django.urls import path, include
from .controllers.websocket_controller import websocket_status, clear_websocket_connections

urlpatterns = [
    path('', include('apps.chat.routes.chat_routes')),
    path('websocket/status/', websocket_status, name='websocket-status'),
    path('websocket/clear/', clear_websocket_connections, name='websocket-clear'),
]