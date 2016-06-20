# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flightinfosystem', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='flights',
            name='timeexp',
            field=models.DateTimeField(verbose_name='Время расчетное', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='flights',
            name='timefact',
            field=models.DateTimeField(verbose_name='Время по факту', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='flights',
            name='timeplan',
            field=models.DateTimeField(verbose_name='Время по плану', null=True, blank=True),
        ),
    ]
