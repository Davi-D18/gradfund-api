from django.contrib import admin
from apps.academic.models.academics import Universidade, Curso


@admin.register(Universidade)
class UniversidadesAdmin(admin.ModelAdmin):
    list_display = ("nome", "sigla")
    search_fields = ("nome", "sigla")
    list_filter = ("nome", "cidade")


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ("nome",)
    search_fields = ("nome",)
    list_filter = ("nome",)