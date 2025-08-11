from django.urls import re_path
from .consumers.chat_consumer import ChatConsumer
from .consumers.user_consumer import UserConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_id>\d+)/$', ChatConsumer.as_asgi()),
    re_path(r'ws/user/(?P<user_id>\d+)/$', UserConsumer.as_asgi()),
]