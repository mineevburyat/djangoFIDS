# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flightinfosystem', '0003_flightsstatus'),
    ]

    operations = [
        migrations.AddField(
            model_name='flights',
            name='portdist',
            field=models.CharField(blank=True, verbose_name='Аэропорты', max_length=100),
        ),
        migrations.AddField(
            model_name='flights',
            name='punktdist',
            field=models.CharField(blank=True, verbose_name='Маршрут', max_length=100),
        ),
    ]
