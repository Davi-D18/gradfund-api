from django.db import models
from apps.authentication.models import CustomerUser
from apps.services.models.services import Service


class ChatRoom(models.Model):
    participantes = models.ManyToManyField(CustomerUser, related_name='salas_chat')
    servico = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='salas_chat')
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    ativo = models.BooleanField(default=True)
    ultima_mensagem_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-atualizado_em']
        verbose_name = 'Sala de Chat'
        verbose_name_plural = 'Salas de Chat'

    def __str__(self):
        return f"Chat - {self.servico.titulo}"


class Message(models.Model):
    TIPOS_MENSAGEM = [
        ('text', 'Texto'),
        ('image', 'Imagem'),
        ('file', 'Arquivo'),
    ]

    sala_chat = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='mensagens')
    remetente = models.ForeignKey(CustomerUser, on_delete=models.CASCADE, related_name='mensagens_enviadas')
    conteudo = models.TextField()
    tipo_mensagem = models.CharField(max_length=10, choices=TIPOS_MENSAGEM, default='text')
    enviado_em = models.DateTimeField(auto_now_add=True)
    lida = models.BooleanField(default=False)
    entregue_em = models.DateTimeField(null=True, blank=True)
    lida_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['enviado_em']
        verbose_name = 'Mensagem'
        verbose_name_plural = 'Mensagens'

    def __str__(self):
        return f"{self.remetente.usuario.username}: {self.conteudo[:50]}"