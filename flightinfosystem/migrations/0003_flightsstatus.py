# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flightinfosystem', '0002_auto_20160619_2027'),
    ]

    operations = [
        migrations.CreateModel(
            name='FlightsStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('statuscheckin', models.BooleanField(default=False, verbose_name='Статус регистрации пассажиров')),
                ('statusboard', models.BooleanField(default=False, verbose_name='Статус посадки пассажиров')),
                ('statusbaggage', models.BooleanField(default=False, verbose_name='Статус выдачи багажа')),
                ('checkins', models.CharField(verbose_name='Используемые стойки регистрации', blank=True, max_length=13)),
                ('gate', models.CharField(verbose_name='Используемый выход для посадки', blank=True, max_length=4)),
                ('baggage', models.CharField(verbose_name='Используемая лента выдачи багажа', blank=True, max_length=4)),
                ('fly', models.ForeignKey(verbose_name='Рейс', to='flightinfosystem.Flights')),
            ],
        ),
    ]
