# Generated by Django 5.1.4 on 2024-12-13 18:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('local', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ocorrencia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('insc', models.IntegerField()),
                ('status', models.CharField(choices=[('fogo', 'Fogo'), ('lixo', 'Lixo'), ('null', 'Sem status')], default='null', max_length=4)),
                ('desc', models.TextField()),
                ('noti', models.BooleanField(default=False)),
                ('nsc', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='local.local')),
            ],
        ),
    ]
