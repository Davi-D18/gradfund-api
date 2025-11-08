from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='payout_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='payout_attempts',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='payment',
            name='payout_completed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='payout_last_error',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='payout_requested_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='payout_status',
            field=models.CharField(
                choices=[
                    ('awaiting_info', 'Aguardando dados do prestador'),
                    ('ready', 'Pronto para transferência'),
                    ('in_progress', 'Transferência em andamento'),
                    ('completed', 'Transferência concluída'),
                    ('failed', 'Falha na transferência'),
                ],
                default='awaiting_info',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='payment',
            name='payout_transaction_id',
            field=models.CharField(blank=True, max_length=120, null=True),
        ),
        migrations.AddField(
            model_name='payment',
            name='valor_plataforma',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='payment',
            name='valor_prestador',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]
