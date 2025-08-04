from django.contrib import admin
from django.contrib import messages
from apps.academic.models.academics import Universidade, Curso


@admin.register(Universidade)
class UniversidadesAdmin(admin.ModelAdmin):
    list_display = ("nome", "sigla", "cidade", "estado")
    search_fields = ("nome", "sigla")
    list_filter = ("cidade", "estado")
    

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ("nome",)
    search_fields = ("nome",)