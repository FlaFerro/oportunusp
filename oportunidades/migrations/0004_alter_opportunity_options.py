# Generated by Django 5.1.3 on 2024-11-15 23:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('oportunidades', '0003_alter_opportunity_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='opportunity',
            options={'permissions': [('can_create', 'Can create opportunity'), ('can_edit', 'Can edit opportunity'), ('can_delete', 'Can delete opportunity'), ('can_view', 'Can view opportunity')]},
        ),
    ]
