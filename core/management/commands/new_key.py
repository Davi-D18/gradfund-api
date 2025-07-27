from django.core.management.base import BaseCommand
from django.core.management.utils import get_random_secret_key


class Command(BaseCommand):
    help = 'Gera uma nova chave secreta para o Django'

    def handle(self, *args, **options):
        secret_key = get_random_secret_key()
        self.stdout.write(
            self.style.SUCCESS(f'Nova chave secreta gerada:\n{secret_key}')
        )