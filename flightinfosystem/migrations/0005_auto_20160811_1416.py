# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flightinfosystem', '0004_auto_20160802_2242'),
    ]

    operations = [
        migrations.AddField(
            model_name='board',
            name='endtime',
            field=models.DateTimeField(null=True, verbose_name='Конец посадки', blank=True),
        ),
        migrations.AddField(
            model_name='board',
            name='starttime',
            field=models.DateTimeField(null=True, verbose_name='Начало посадки', blank=True),
        ),
    ]
