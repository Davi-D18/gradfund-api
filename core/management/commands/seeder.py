from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import importlib.util
import os
import sys
import hashlib
import json
from core.models import SeederExecution

class Command(BaseCommand):
    help = 'Executa seeders de um app específico'
    
    def add_arguments(self, parser):
        parser.add_argument('app_name', nargs='?', type=str, help='Nome do app')
        parser.add_argument('seeder_name', nargs='?', type=str, help='Nome do seeder específico')
        parser.add_argument('--all', action='store_true', help='Executar todos os seeders')
        parser.add_argument('--check', action='store_true', help='Verificar status sem executar')
        parser.add_argument('--force', action='store_true', help='Forçar execução mesmo se já aplicado')
    
    def handle(self, *args, **options):
        # Adicionar paths necessários
        project_root = settings.BASE_DIR
        apps_dir = os.path.join(project_root, 'apps')
        
        for path in [project_root, apps_dir]:
            if path not in sys.path:
                sys.path.insert(0, path)
        
        if options['all']:
            self.run_all_seeders(options)
        elif options['app_name']:
            self.run_app_seeders(options['app_name'], options['seeder_name'], options)
        else:
            raise CommandError('Informe o nome do app ou use --all')
    
    def run_all_seeders(self, options):
        """Executa todos os seeders do projeto"""
        seeders_dir = os.path.join(settings.BASE_DIR, 'seeders')
        
        if not os.path.exists(seeders_dir):
            raise CommandError(f"Diretório seeders não encontrado: {seeders_dir}")
        
        for app_name in os.listdir(seeders_dir):
            app_path = os.path.join(seeders_dir, app_name)
            if os.path.isdir(app_path):
                self.stdout.write(f"\n{'='*50}")
                self.stdout.write(f"Processando app: {app_name}")
                try:
                    self.run_app_seeders(app_name, None, options)
                except CommandError as e:
                    self.stdout.write(self.style.ERROR(str(e)))
    
    def run_app_seeders(self, app_name, seeder_name, options):
        """Executa seeders de um app específico"""
        app_dir = os.path.join(settings.BASE_DIR, 'seeders', app_name)
        
        if not os.path.exists(app_dir):
            raise CommandError(f"Pasta não encontrada: {app_dir}")
        
        # Buscar arquivos .py
        seeder_files = [f for f in os.listdir(app_dir) if f.endswith('.py') and f != '__init__.py']
        
        if not seeder_files:
            raise CommandError(f"Nenhum seeder encontrado em {app_dir}")
        
        # Se seeder específico foi informado
        if seeder_name:
            seeder_file = f"{seeder_name}.py"
            if seeder_file not in seeder_files:
                raise CommandError(f"Seeder {seeder_name} não encontrado em {app_name}")
            seeder_files = [seeder_file]
        
        # Executar seeders
        for seeder_file in seeder_files:
            self.execute_seeder(app_dir, seeder_file, options)
    
    def execute_seeder(self, app_dir, seeder_file, options):
        """Executa um arquivo seeder específico com controle de execução"""
        seeder_path = os.path.join(app_dir, seeder_file)
        seeder_name = os.path.splitext(seeder_file)[0]
        app_name = os.path.basename(app_dir)
        
        # Calcular hash dos dados
        data_hash = self.calculate_data_hash(app_dir, seeder_name)
        
        # Verificar se já foi executado
        execution, created = SeederExecution.objects.get_or_create(
            app_label=app_name,
            seeder_name=seeder_name,
            defaults={'data_hash': data_hash}
        )
        
        status_message = f"Seeder {seeder_name} - "
        if created:
            status_message += "NUNCA EXECUTADO"
        elif execution.data_hash != data_hash:
            status_message += "DADOS ALTERADOS"
        else:
            status_message += "JÁ EXECUTADO"
        
        if options['check']:
            self.stdout.write(self.style.WARNING(status_message))
            return
        
        # Se já foi executado com os mesmos dados, pular (exceto se --force)
        if not created and execution.data_hash == data_hash and not options.get('force'):
            self.stdout.write(self.style.WARNING(
                f"✓ {seeder_name} já foi aplicado com os dados atuais. Use --force para reexecutar"
            ))
            return
        
        try:
            # Carregar e executar módulo
            spec = importlib.util.spec_from_file_location(seeder_name, seeder_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[seeder_name] = module
            spec.loader.exec_module(module)
            
            if not hasattr(module, 'Command'):
                raise CommandError(f"Seeder {seeder_name} não contém classe Command")
            
            # Executar seeder
            self.stdout.write(f"Executando: {seeder_name}")
            seeder_command = module.Command()
            seeder_command.stdout = self.stdout
            seeder_command.stderr = self.stderr
            seeder_command.handle()
            
            # Atualizar hash após execução
            execution.data_hash = data_hash
            execution.save()
            
            self.stdout.write(self.style.SUCCESS(f"✓ {seeder_name} executado e registrado com sucesso"))
            
        except Exception as e:
            raise CommandError(f"Erro ao executar {seeder_name}: {str(e)}")
    
    def calculate_data_hash(self, app_dir, seeder_name):
        """Calcula hash dos dados JSON para detectar alterações"""
        data_dir = os.path.join(app_dir, 'data')
        if not os.path.exists(data_dir):
            return "no-data"
        
        hasher = hashlib.sha256()
        
        # Processar arquivos JSON relacionados ao seeder
        json_files = []
        
        # Procurar arquivo JSON com mesmo nome do seeder
        seeder_json = os.path.join(data_dir, f"{seeder_name.replace('_seeder', '')}.json")
        if os.path.exists(seeder_json):
            json_files.append(seeder_json)
        else:
            # Se não encontrar, processar todos os JSONs
            json_files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith('.json')]
        
        for json_file in json_files:
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    # Usar sort_keys para garantir consistência
                    hasher.update(json.dumps(data, sort_keys=True).encode('utf-8'))
            except (json.JSONDecodeError, FileNotFoundError):
                continue
        
        return hasher.hexdigest()