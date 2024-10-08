# Generated by Django 5.1 on 2024-08-11 21:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Session',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True)),
                ('code', models.CharField(max_length=10, primary_key=True, serialize=False, unique=True)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('restaurants', models.JSONField(blank=True, default=list)),
                ('count', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='SessionUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=100)),
                ('rankings', models.JSONField(blank=True, default=dict)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users', to='rankerapi.session')),
            ],
        ),
    ]
