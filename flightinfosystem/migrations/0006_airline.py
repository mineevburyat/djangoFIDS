# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flightinfosystem', '0005_auto_20160811_1416'),
    ]

    operations = [
        migrations.CreateModel(
            name='Airline',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('cod_iata', models.CharField(max_length=2, verbose_name='Код авиакомпании IATA')),
                ('cod_icao', models.CharField(max_length=3, verbose_name='Код авиакомпании ICAO')),
                ('name', models.CharField(max_length=25, verbose_name='Полное наименование')),
                ('biglogo', models.ImageField(upload_to='biglogo/', height_field=600, width_field=800, verbose_name='Большой логотип')),
                ('smallogo', models.ImageField(upload_to='smallogo/', height_field=60, width_field=80, verbose_name='Малый логотип')),
            ],
        ),
    ]
