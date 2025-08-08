from django.contrib import admin
from .models import ChatRoom, Message


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['servico', 'criado_em', 'ativo', 'ultima_mensagem_em']
    list_filter = ['ativo', 'criado_em']
    search_fields = ['servico__title']
    readonly_fields = ['criado_em', 'atualizado_em']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['remetente', 'sala_chat', 'conteudo', 'enviado_em', 'lida']
    list_filter = ['tipo_mensagem', 'lida', 'enviado_em']
    search_fields = ['conteudo', 'remetente__username']
    readonly_fields = ['enviado_em', 'entregue_em', 'lida_em']