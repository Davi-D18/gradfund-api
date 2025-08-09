from django.urls import re_path
from .consumers.simple_consumer import SimpleChatConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_id>\d+)/$', SimpleChatConsumer.as_asgi()),
]