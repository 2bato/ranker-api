# Generated by Django 5.1 on 2024-08-11 21:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rankerapi', '0003_alter_session_restaurants'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='count',
            field=models.IntegerField(default=0),
            preserve_default=False,
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
