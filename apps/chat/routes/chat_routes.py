from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from apps.chat.controllers.chat_controller import ChatRoomViewSet
from apps.chat.controllers.message_controller import MessageViewSet

# Router principal para salas de chat
router = DefaultRouter()
router.register(r'rooms', ChatRoomViewSet, basename='chatroom')

# Router aninhado para mensagens dentro das salas
rooms_router = routers.NestedDefaultRouter(router, r'rooms', lookup='room')
rooms_router.register(r'messages', MessageViewSet, basename='room-messages')

# URLs combinadas
urlpatterns = router.urls + rooms_router.urls