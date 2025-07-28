from django.db import models
from apps.authentication.models import CustomerUser


class TypeService(models.Model):
    nome = models.CharField(max_length=120)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Tipo de Serviço'
        verbose_name_plural = 'Tipos de Serviços'

    def __str__(self):
        return self.nome



class Service(models.Model):
    estudante = models.ForeignKey(CustomerUser, on_delete=models.CASCADE, related_name='services_customer_user')
    titulo = models.CharField(max_length=120)
    descricao = models.TextField()
    tipo_servico = models.ForeignKey(TypeService, on_delete=models.PROTECT, related_name='services_type_service')
    preco = models.IntegerField()
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    ativo = models.BooleanField(default=True)


    class Meta:
        ordering = ['titulo']
        verbose_name = 'Serviço'
        verbose_name_plural = 'Serviços'

    def __str__(self):
        return f"{self.titulo} - {self.estudante.usuario.username}" 
