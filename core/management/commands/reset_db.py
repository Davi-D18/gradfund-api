import os
from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = 'Reseta o banco de dados (remove migrations e recria)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirma a operação sem perguntar'
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            confirm = input('Isso irá deletar TODOS os dados. Continuar? (s/N): ')
            if confirm.lower() != 's':
                self.stdout.write('Operação cancelada.')
                return

        # Remove migrations
        for root, dirs, files in os.walk('apps'):
            if 'migrations' in dirs:
                migrations_path = os.path.join(root, 'migrations')
                for file in os.listdir(migrations_path):
                    if file.endswith('.py') and file != '__init__.py':
                        os.remove(os.path.join(migrations_path, file))

        # Remove database
        if os.path.exists('database.db'):
            os.remove('database.db')

        # Recreate migrations and database
        call_command('makemigrations')
        call_command('migrate')
        
        self.stdout.write(
            self.style.SUCCESS('Banco de dados resetado com sucesso!')
        )