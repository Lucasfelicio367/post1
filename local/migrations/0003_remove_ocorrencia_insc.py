# Generated by Django 5.1.4 on 2024-12-13 18:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('local', '0002_ocorrencia'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ocorrencia',
            name='insc',
        ),
    ]
