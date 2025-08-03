from django.db import models
from utils.formatters import StringFormatter


class Universidade(models.Model):
    nome = models.CharField(max_length=255, blank=True, null=True)
    sigla = models.CharField(max_length=20, blank=True, null=True, unique=True)
    cidade = models.CharField(max_length=40, blank=True, null=True)
    estado = models.CharField(max_length=25, blank=True, null=True)

    def clean(self):
        if self.nome:
            self.nome = StringFormatter.format_text(self.nome, 'strip')
        if self.sigla:
            self.sigla = StringFormatter.format_text(self.sigla, 'strip')
        if self.cidade:
            self.cidade = StringFormatter.format_text(self.cidade, 'strip')
        if self.estado:
            self.estado = StringFormatter.format_text(self.estado, 'strip')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Universidade'
        verbose_name_plural = 'Universidades'

    def __str__(self):
        return self.nome


class Curso(models.Model):
    nome = models.CharField(max_length=200, blank=True, null=True)

    def clean(self):
        if self.nome:
            self.nome = StringFormatter.format_text(self.nome, 'strip')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'

    def __str__(self):
        return self.nome
