from django.db import models


class Universidade(models.Model):
    nome = models.CharField(max_length=255, blank=True, null=True)
    sigla = models.CharField(max_length=20, blank=True, null=True, unique=True)
    cidade = models.CharField(max_length=40, blank=True, null=True)
    estado = models.CharField(max_length=25, blank=True, null=True)


    class Meta:
        ordering = ['nome']
        verbose_name = 'Universidade'
        verbose_name_plural = 'Universidades'

    def __str__(self):
        return self.nome


class Curso(models.Model):
    nome = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        ordering = ['nome']
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'

    def __str__(self):
        return self.nome
