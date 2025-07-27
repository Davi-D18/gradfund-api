import os
import shutil

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Cria um novo app com a estrutura de diretórios do projeto e scaffolds de API'
    missing_args_message = "Você precisa fornecer o nome do app."

    def add_arguments(self, parser):
        parser.add_argument('name', help='Nome do app')
        parser.add_argument(
            'resource',
            nargs='?',
            help='Nome do recurso (singular ou plural) para gerar schemas, services, repository, routes e controllers'
        )

    def handle(self, **options):
        app_name = options.pop('name')
        resource = (options.pop('resource') or app_name).lower().strip()

        # Define singular e plural
        if resource.endswith('s'):
            singular = resource[:-1]
            plural = resource
        else:
            singular = resource
            plural = f"{resource}s"

        app_dir = os.path.join('apps', app_name)

        # Cria a pasta 'apps/' e a pasta do app explicitamente
        os.makedirs(app_dir, exist_ok=True)  # Garante que 'apps/' existe

        try:
            # Cria o app usando o comando startapp padrão do Django
            call_command('startapp', app_name, app_dir)
        except Exception as e:
            raise CommandError(f'Erro ao criar app: {e}')

        try:
            self._create_directories(app_dir)
            self._move_default_files(app_dir, plural)
            self._create_scaffold_files(app_dir, singular, plural)
            self._update_apps_py(app_dir, app_name)
            self._create_readme(app_dir, app_name)
            self._create_urls_py(app_dir, plural)
            self._print_success(app_name, resource)
            self._modify_controllers(app_dir, singular, plural)
            self._modify_models(app_dir, plural)
        except Exception as e:
            shutil.rmtree(app_dir, ignore_errors=True)
            raise CommandError(f'Erro ao configurar o app: {e}')

    def _create_directories(self, base_dir):
        folders = [
            'controllers', 'models', 'schemas', 'services',
            'routes',
            'tests/controllers', 'tests/models', 'tests/services',
        ]
        for folder in folders:
            path = os.path.join(base_dir, folder)
            os.makedirs(path, exist_ok=True)
            open(os.path.join(path, '__init__.py'), 'w').close()

    def _move_default_files(self, base_dir, plural):
        moves = {
            'models.py': os.path.join('models', f'{plural}.py'),
            'views.py': os.path.join('controllers', f'{plural}_controller.py'),
            'tests.py': os.path.join('tests', '__init__.py'),
        }
        for src, dst in moves.items():
            src_path = os.path.join(base_dir, src)
            dst_path = os.path.join(base_dir, dst)
            if os.path.exists(src_path):
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                shutil.move(src_path, dst_path)

    def _create_scaffold_files(self, base_dir, singular, plural):
        templates = {
            os.path.join('schemas', f'{singular}_schema.py'): self._template_schema(singular, plural),
            os.path.join('services', f'{plural}_service.py'): self._template_service(),
            os.path.join('routes', f'{plural}_routes.py'): self._template_routes(plural),
        }
        for rel_path, content in templates.items():
            full_path = os.path.join(base_dir, rel_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            if not os.path.exists(full_path):
                with open(full_path, 'w') as f:
                    f.write(content)

    def _update_apps_py(self, base_dir, app_name):
        apps_file = os.path.join(base_dir, 'apps.py')
        with open(apps_file, 'r') as f:
            content = f.read()
        content = content.replace(
            f"name = '{app_name}'",
            f"name = 'apps.{app_name}'"
        )
        with open(apps_file, 'w') as f:
            f.write(content)

    def _create_readme(self, base_dir, app_name):
        content = f"""# {app_name.title()} App

Este é um app do projeto {app_name}.

## Estrutura do App
```
{app_name}/
├── controllers/     # Views e ViewSets
├── models/          # Modelos do Django
├── schemas/         # Schemas para validação
├── services/        # Lógica de negócio
├── repository/      # Camada de acesso a dados
├── routes/          # URLs e ViewSets
└── tests/           # Testes unitários
```

## Comandos Úteis

### Migrações
```bash
python manage.py makemigrations {app_name}
python manage.py migrate
```

### Testes
```bash
python manage.py test apps.{app_name}
python manage.py test apps.{app_name}.tests.controllers
```
"""
        with open(os.path.join(base_dir, 'README.md'), 'w') as f:
            f.write(content)

    def _create_urls_py(self, base_dir, plural):
        content = f"""from django.urls import path, include


urlpatterns = [
    path('', include('apps.{plural}.routes.{plural}_routes')),
]
"""
        with open(os.path.join(base_dir, 'urls.py'), 'w') as f:
            f.write(content)

    def _print_success(self, app_name, resource):
        msg = (
            f'App "{app_name}" criado com sucesso em apps/{app_name}/\n'
            f'Scaffold de recurso "{resource}" adicionado.'
        )
        self.stdout.write(self.style.SUCCESS(msg))

    def _template_schema(self, singular, plural):
        class_name = singular.capitalize()
        return f"""
from rest_framework import serializers
from apps.{plural}.models.{plural} import {plural.capitalize()}

class {class_name}Serializer(serializers.ModelSerializer):
    class Meta:
        model = {plural.capitalize()}
        fields = '__all__'
"""

    def _template_service(self):
        return (
            "# Implemente aqui a lógica de negócio para o recurso\n"
        )

    def _template_routes(self, plural):
        class_name = plural.capitalize()
        return "\n".join([
            "from django.urls import path, include",
            "from rest_framework.routers import DefaultRouter",
            f"from apps.{plural}.controllers.{plural}_controller import {class_name}ViewSet",
            "",

            "router = DefaultRouter()",
            f"router.register('{plural}', {class_name}ViewSet)",
            "",
            "urlpatterns = [",
            "    path('', include(router.urls))",
            "]"
        ])

    def _modify_controllers(self, base_dir, singular, plural):
        controllers_dir = os.path.join(base_dir, 'controllers')
        class_name = singular.capitalize()

        content = f"""from rest_framework.viewsets import ModelViewSet

from apps.{plural}.schemas.{singular}_schema import {class_name}Serializer
from apps.{plural}.models.{plural} import {plural.capitalize()}

class {plural.capitalize()}ViewSet(ModelViewSet):
    queryset = {plural.capitalize()}.objects.all()
    serializer_class = {singular.capitalize()}Serializer
"""

        for filename in os.listdir(controllers_dir):
            if filename.endswith('_controller.py'):
                file_path = os.path.join(controllers_dir, filename)
                with open(file_path, 'a') as f:
                    f.write(content) 

    def _modify_models(self, base_dir, plural):
        models_dir = os.path.join(base_dir, 'models')
        class_name = plural.capitalize()

        content = f"""

class {class_name}(models.Model):
    # adicione aqui os demais campos

    class Meta:
        ordering = ['name']
        verbose_name = '' # nome da tabela no banco

    def __str__(self):
        return self.name # Exibe o campo name
"""

        for filename in os.listdir(models_dir):
            if filename.endswith(f'{plural}.py'):
                file_path = os.path.join(models_dir, filename)
                with open(file_path, 'a') as f:
                    f.write(content)

