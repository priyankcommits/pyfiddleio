# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-01-28 17:13
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pyfiddleweb', '0006_auto_20171230_1833'),
    ]

    operations = [
        migrations.AddField(
            model_name='script',
            name='date',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now),
        ),
        migrations.AddField(
            model_name='script',
            name='last_edit',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
    ]
