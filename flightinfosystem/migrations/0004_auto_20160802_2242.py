# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flightinfosystem', '0003_auto_20160802_0032'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='checkin',
            name='deltastartcheckin',
        ),
        migrations.RemoveField(
            model_name='checkin',
            name='deltastopcheckin',
        ),
        migrations.AddField(
            model_name='checkin',
            name='startcheckin',
            field=models.DateTimeField(verbose_name='Начало регистрации', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='checkin',
            name='stopcheckin',
            field=models.DateTimeField(verbose_name='Конец регистрации', null=True, blank=True),
        ),
    ]
