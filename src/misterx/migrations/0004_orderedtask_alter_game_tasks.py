# Generated by Django 5.1.7 on 2025-03-30 21:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('misterx', '0003_alter_submission_points_override'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderedTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('task_number', models.IntegerField(blank=True, null=True, verbose_name='Task number')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='misterx.game')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='misterx.task')),
            ],
        ),
        migrations.RemoveField(
            model_name='game',
            name='tasks',
        ),
        migrations.AddField(
            model_name='game',
            name='tasks',
            field=models.ManyToManyField(blank=True, related_name='games', through='misterx.OrderedTask', to='misterx.task'),
        ),
    ]
