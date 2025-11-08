from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_customeruser_mp_access_token_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customeruser',
            name='pix_key',
            field=models.CharField(blank=True, max_length=120, null=True),
        ),
        migrations.AddField(
            model_name='customeruser',
            name='pix_key_type',
            field=models.CharField(
                blank=True,
                choices=[
                    ('cpf', 'CPF'),
                    ('cnpj', 'CNPJ'),
                    ('email', 'E-mail'),
                    ('phone', 'Telefone'),
                    ('random', 'Chave Aleatória'),
                ],
                max_length=20,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='customeruser',
            name='payout_account_holder_document',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='customeruser',
            name='payout_account_holder_name',
            field=models.CharField(blank=True, max_length=120, null=True),
        ),
        migrations.AddField(
            model_name='customeruser',
            name='payout_bank_account',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='customeruser',
            name='payout_bank_account_type',
            field=models.CharField(
                blank=True,
                choices=[
                    ('checking', 'Conta Corrente'),
                    ('savings', 'Conta Poupança'),
                    ('payment', 'Conta de Pagamento'),
                ],
                max_length=20,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='customeruser',
            name='payout_bank_branch',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='customeruser',
            name='payout_bank_code',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='customeruser',
            name='payout_last_updated_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='customeruser',
            name='preferred_payout_method',
            field=models.CharField(
                choices=[
                    ('pix', 'PIX'),
                    ('bank_transfer', 'Transferência Bancária'),
                ],
                default='pix',
                max_length=20,
            ),
            preserve_default=False,
        ),
    ]
