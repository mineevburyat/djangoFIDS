# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Flights',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('fly', models.CharField(max_length=9, verbose_name='Рейс')),
                ('ad', models.IntegerField(verbose_name='Направление')),
                ('aircraft', models.CharField(max_length=10, verbose_name='Тип ВС')),
                ('carrname', models.CharField(max_length=35, verbose_name='Перевозчик')),
                ('status', models.CharField(max_length=60, verbose_name='Статус рейса из AODB', blank=True)),
            ],
        ),
    ]
