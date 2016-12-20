# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('flightinfosystem', '0002_auto_20160802_0026'),
    ]

    operations = [
        migrations.AlterField(
            model_name='board',
            name='boardfly',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='flightinfosystem.Flight', null=True, blank=True, verbose_name='Рейс'),
        ),
    ]
