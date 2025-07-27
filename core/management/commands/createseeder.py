import os
import json
import re
from django.core.management.base import BaseCommand, CommandError
from django.apps import apps

class Command(BaseCommand):
    help = 'Cria um arquivo seeder para um modelo específico com organização em pastas'
    
    def add_arguments(self, parser):
        parser.add_argument('app_model', type=str, 
                           help='Nome no formato App.Model (ex: auth.User)')
        parser.add_argument('--quantity', type=int, default=5,
                           help='Quantidade de exemplos a gerar (padrão: 5)')
        parser.add_argument('--update', action='store_true',
                           help='Atualizar seeder existente mantendo dados personalizados')

    def handle(self, *args, **options):
        try:
            app_label, model_name = options['app_model'].split('.')
        except ValueError:
            raise CommandError('Formato inválido. Use App.Model (ex: auth.User)')
        
        # Validar se o modelo existe
        try:
            model = apps.get_model(app_label, model_name)
        except LookupError:
            raise CommandError(f'Modelo {model_name} não encontrado no app {app_label}')
        
        # Criar estrutura de diretórios
        base_dir = 'seeders'
        app_dir = os.path.join(base_dir, app_label)
        data_dir = os.path.join(app_dir, 'data')
        
        os.makedirs(data_dir, exist_ok=True)
        
        # Nome do arquivo seeder
        seeder_file = os.path.join(app_dir, f'{model_name.lower()}_seeder.py')
        
        # Se for atualização, manter os dados existentes
        existing_data = []
        if options['update'] and os.path.exists(seeder_file):
            with open(seeder_file, 'r') as f:
                content = f.read()
                # Extrair dados existentes usando regex
                data_match = re.search(r"# SEED DATA START\n(.*?)# SEED DATA END", 
                                      content, re.DOTALL)
                if data_match:
                    existing_data = data_match.group(1).strip().split('\n')
        
        # Gerar conteúdo do seeder
        seeder_content = self.generate_seeder_content(
            model, 
            options['quantity'], 
            options['app_model'],
            existing_data
        )
        
        # Escrever o arquivo seeders.py
        with open(seeder_file, 'w') as f:
            f.write(seeder_content)
        
        # Criar/atualizar arquivo JSON de dados
        json_file = os.path.join(data_dir, f"{model_name}.json")
        if not os.path.exists(json_file) or options['update']:
            json_content = self.generate_json_data(model, options['quantity'])
            with open(json_file, 'w') as f:
                json.dump(json_content, f, indent=4)
        
        self.stdout.write(self.style.SUCCESS(
            f"Seeder criado com sucesso!\n"
            f"  - Seeder: {seeder_file}\n"
            f"  - Dados: {json_file}\n\n"
            "Edite o arquivo JSON para adicionar dados personalizados."
        ))

    def generate_seeder_content(self, model, quantity, model_name, existing_data=[]):
        """Gera o conteúdo do arquivo seeders.py dinâmico"""
        model_name = model.__name__
        app_label = model._meta.app_label
        
        # Gerar campos dinamicamente
        unique_fields, defaults_fields, fk_fields = self.analyze_model_fields(model)
        
        return f"""
import os
import json
from django.core.management.base import BaseCommand
from apps.{app_label}.models import {model_name}

class Command(BaseCommand):
    help = 'Popula a tabela {model_name} com dados iniciais'

    def handle(self, *args, **options):
        self.load_data_from_json('{model_name.lower()}.json')
        
        self.stdout.write(self.style.SUCCESS(
            "Dados de {model_name} carregados com sucesso!"
        ))
    
    def load_data_from_json(self, filename):
        \"\"\"Carrega dados de um arquivo JSON\"\"\"
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_dir, 'data', filename)
        
        if not os.path.exists(data_path):
            self.stdout.write(self.style.WARNING(
                f"Arquivo de dados não encontrado: {{data_path}}"
            ))
            return
        
        with open(data_path, 'r') as f:
            data = json.load(f)
        
        created_count = 0
        for item in data:
            try:
                # Campos únicos para get_or_create
                unique_data = {{{unique_fields}}}
                
                # Campos padrão (incluindo ForeignKeys)
                defaults_data = {{{defaults_fields}}}
                
                obj, created = {model_name}.objects.get_or_create(
                    **unique_data,
                    defaults=defaults_data
                )
                if created:
                    created_count += 1
            except Exception as e:
                self.stdout.write(self.style.WARNING(
                    f"Erro ao criar registro: {{str(e)}}"
                ))
        
        self.stdout.write(self.style.SUCCESS(
            f"{{created_count}} registros de {model_name} criados a partir de {{filename}}"
        ))
"""

    def generate_json_data(self, model, quantity):
        """Gera dados de exemplo em formato JSON"""
        examples = []
        
        for i in range(quantity):
            example = {}
            for field in model._meta.fields:
                if field.name == 'id':
                    continue
                    
                field_type = field.get_internal_type()
                example[field.name] = self.get_field_example(field, field_type)
            
            examples.append(example)
        
        return examples

    def get_field_example(self, field, field_type):
        """Retorna um exemplo baseado no tipo de campo"""
        field_name = field.name
        max_length = getattr(field, 'max_length', None)
        
        examples = {
            'CharField': f"Texto {field_name}" + (f" (max {max_length})" if max_length else ""),
            'TextField': "Texto longo para descrição ou conteúdo",
            'IntegerField': 42,
            'BooleanField': True,
            'DateField': "2023-01-15",
            'DateTimeField': "2023-01-15T12:30:00Z",
            'EmailField': "email@example.com",
            'ForeignKey': 1,  # ID de objeto relacionado
            'DecimalField': "10.99",
            'FloatField': 3.14,
            'URLField': "https://exemplo.com",
        }
        
        return examples.get(field_type, None)
    
    def analyze_model_fields(self, model):
        """Analisa campos do modelo para gerar código dinâmico"""
        unique_fields = []
        defaults_fields = []
        fk_fields = []
        
        for field in model._meta.fields:
            if field.name in ['id', 'created_at', 'updated_at']:
                continue
                
            field_code = f"'{field.name}': item.get('{field.name}')"
            
            if field.get_internal_type() == 'ForeignKey':
                field_code = f"'{field.name}_id': item.get('{field.name}')"
                defaults_fields.append(field_code)
                fk_fields.append(field.name)
            elif field.unique or field.name in ['title', 'name', 'email']:
                unique_fields.append(field_code)
            else:
                defaults_fields.append(field_code)
        
        # Se não há campos únicos, usar o primeiro campo disponível
        if not unique_fields and defaults_fields:
            unique_fields.append(defaults_fields.pop(0))
        
        unique_str = ',\n                    '.join(unique_fields) if unique_fields else "'id': item.get('id')"
        defaults_str = ',\n                    '.join(defaults_fields) if defaults_fields else ""
        
        return unique_str, defaults_str, fk_fields