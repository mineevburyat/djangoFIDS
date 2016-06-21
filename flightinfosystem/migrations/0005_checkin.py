# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flightinfosystem', '0004_auto_20160619_1426'),
    ]

    operations = [
        migrations.CreateModel(
            name='Checkin',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('num', models.IntegerField(verbose_name='Номер стойки')),
                ('fullname', models.CharField(verbose_name='Полное имя стойки', max_length=21)),
                ('shortname', models.CharField(verbose_name='Короткое имя стойки', max_length=5)),
            ],
        ),
    ]
