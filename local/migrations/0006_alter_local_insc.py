# Generated by Django 5.1.4 on 2024-12-28 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('local', '0005_remove_local_owner_ocorrencia_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='local',
            name='insc',
            field=models.CharField(max_length=20),
        ),
    ]
