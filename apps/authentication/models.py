from django.db import models
from django.contrib.auth.models import User
from apps.authentication.constants.user import USER_TYPE_CHOICES
from apps.academic.models.academics import Universidade, Curso
from core.models import UUIDModel


class CustomerUser(UUIDModel):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='usuario_user')
    tipo_usuario = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    universidade = models.ForeignKey(Universidade, on_delete=models.PROTECT, blank=True, null=True)
    curso = models.ForeignKey(Curso, on_delete=models.PROTECT, blank=True, null=True)
    ano_formatura = models.IntegerField(blank=True, null=True)

    class Meta:
        verbose_name = "Perfil de Usuário"
        verbose_name_plural = "Perfis de Usuários"
        
    def __str__(self):
        return self.usuario.username