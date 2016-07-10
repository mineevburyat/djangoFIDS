# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Checkin',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('num', models.CharField(max_length=2, verbose_name='Номер стойки')),
                ('fullname', models.CharField(max_length=21, verbose_name='Полное имя стойки')),
                ('shortname', models.CharField(max_length=5, verbose_name='Короткое имя стойки')),
                ('classcheckin', models.CharField(blank=True, max_length=15, verbose_name='Класс обслуживания')),
                ('deltastartcheckin', models.IntegerField(default=7200, verbose_name='Начало регистрации')),
                ('deltastopcheckin', models.IntegerField(default=2400, verbose_name='Конец регистрации')),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=15, verbose_name='Имя события')),
            ],
        ),
        migrations.CreateModel(
            name='EventLog',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('descript', models.CharField(max_length=60, verbose_name='Допопции события')),
                ('timestamp', models.DateTimeField(auto_now=True, verbose_name='Время события')),
                ('event', models.ForeignKey(to='flightinfosystem.Event', verbose_name='Событие')),
            ],
        ),
        migrations.CreateModel(
            name='Flight',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('fly', models.CharField(max_length=9, verbose_name='Рейс')),
                ('ad', models.IntegerField(verbose_name='Направление')),
                ('punktdist', models.CharField(blank=True, max_length=100, verbose_name='Маршрут')),
                ('portdist', models.CharField(blank=True, max_length=100, verbose_name='Аэропорты по маршруту')),
                ('aircraft', models.CharField(max_length=10, verbose_name='Тип ВС')),
                ('carrname', models.CharField(max_length=35, verbose_name='Перевозчик')),
                ('status', models.CharField(blank=True, max_length=60, verbose_name='Статус рейса из AODB')),
                ('timeplan', models.DateTimeField(blank=True, null=True, verbose_name='Время по плану')),
                ('timeexp', models.DateTimeField(blank=True, null=True, verbose_name='Время расчетное')),
                ('timefact', models.DateTimeField(blank=True, null=True, verbose_name='Время по факту')),
            ],
        ),
        migrations.CreateModel(
            name='FlightStatus',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('checkin', models.BooleanField(default=False, verbose_name='Регистрация пассажиров')),
                ('checkinstop', models.BooleanField(default=False, verbose_name='Конец регистрации')),
                ('board', models.BooleanField(default=False, verbose_name='Статус посадки пассажиров')),
                ('boardstop', models.BooleanField(default=False, verbose_name='Конец посадки пассажиров')),
                ('baggage', models.BooleanField(default=False, verbose_name='Выдача багажа')),
                ('baggagestop', models.BooleanField(default=False, verbose_name='Конец выдачи багажа')),
                ('changeboard', models.BooleanField(default=False, verbose_name='Статус замены борта')),
                ('fly', models.OneToOneField(to='flightinfosystem.Flight', verbose_name='Рейс')),
            ],
        ),
        migrations.AddField(
            model_name='eventlog',
            name='fly',
            field=models.OneToOneField(to='flightinfosystem.Flight', verbose_name='Рейс'),
        ),
        migrations.AddField(
            model_name='checkin',
            name='checkinfly',
            field=models.ForeignKey(to='flightinfosystem.Flight', blank=True, on_delete=django.db.models.deletion.SET_NULL, verbose_name='Рейс', null=True),
        ),
    ]
