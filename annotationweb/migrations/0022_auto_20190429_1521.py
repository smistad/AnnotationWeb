# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2019-04-29 13:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('annotationweb', '0021_task_shuffle_videos'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='shuffle_videos',
            field=models.BooleanField(default=True, help_text='Shuffle videos for annotation task'),
        ),
    ]
