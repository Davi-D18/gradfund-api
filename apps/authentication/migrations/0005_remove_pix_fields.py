# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0004_alter_customeruser_preferred_payout_method'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customeruser',
            name='preferred_payout_method',
        ),
        migrations.RemoveField(
            model_name='customeruser',
            name='pix_key',
        ),
        migrations.RemoveField(
            model_name='customeruser',
            name='pix_key_type',
        ),
        migrations.RemoveField(
            model_name='customeruser',
            name='payout_bank_code',
        ),
        migrations.RemoveField(
            model_name='customeruser',
            name='payout_bank_branch',
        ),
        migrations.RemoveField(
            model_name='customeruser',
            name='payout_bank_account',
        ),
        migrations.RemoveField(
            model_name='customeruser',
            name='payout_bank_account_type',
        ),
        migrations.RemoveField(
            model_name='customeruser',
            name='payout_account_holder_name',
        ),
        migrations.RemoveField(
            model_name='customeruser',
            name='payout_account_holder_document',
        ),
        migrations.RemoveField(
            model_name='customeruser',
            name='payout_last_updated_at',
        ),
    ]