from django.db import models
from django.contrib.auth.models import User
from apps.authentication.constants.user import USER_TYPE_CHOICES
from apps.authentication.constants.payout import (
    BANK_ACCOUNT_TYPE_CHOICES,
    PAYOUT_METHOD_CHOICES,
    PIX_KEY_TYPE_CHOICES,
)
from apps.academic.models.academics import Universidade, Curso
from core.models import UUIDModel


class CustomerUser(UUIDModel):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='usuario_user')
    tipo_usuario = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    universidade = models.ForeignKey(Universidade, on_delete=models.PROTECT, blank=True, null=True)
    curso = models.ForeignKey(Curso, on_delete=models.PROTECT, blank=True, null=True)
    ano_formatura = models.IntegerField(blank=True, null=True)
    preferred_payout_method = models.CharField(
        max_length=20,
        choices=PAYOUT_METHOD_CHOICES,
        default='pix',
    )
    pix_key = models.CharField(max_length=120, blank=True, null=True)
    pix_key_type = models.CharField(max_length=20, choices=PIX_KEY_TYPE_CHOICES, blank=True, null=True)
    payout_bank_code = models.CharField(max_length=20, blank=True, null=True)
    payout_bank_branch = models.CharField(max_length=20, blank=True, null=True)
    payout_bank_account = models.CharField(max_length=30, blank=True, null=True)
    payout_bank_account_type = models.CharField(
        max_length=20,
        choices=BANK_ACCOUNT_TYPE_CHOICES,
        blank=True,
        null=True,
    )
    payout_account_holder_name = models.CharField(max_length=120, blank=True, null=True)
    payout_account_holder_document = models.CharField(max_length=20, blank=True, null=True)
    payout_last_updated_at = models.DateTimeField(blank=True, null=True)


    class Meta:
        verbose_name = "Perfil de Usuário"
        verbose_name_plural = "Perfis de Usuários"
        
    def __str__(self):
        return self.usuario.username