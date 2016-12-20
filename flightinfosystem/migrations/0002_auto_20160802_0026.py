# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flightinfosystem', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Board',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('num', models.CharField(verbose_name='Номер выхода', max_length=2)),
                ('fullname', models.CharField(verbose_name='Имя терминала', max_length=21)),
                ('shortname', models.CharField(verbose_name='Имя выхода', max_length=8)),
                ('boardfly', models.ForeignKey(verbose_name='Рейс', to='flightinfosystem.Flight')),
            ],
        ),
        migrations.AlterField(
            model_name='checkin',
            name='fullname',
            field=models.CharField(verbose_name='Имя терминала', max_length=21),
        ),
    ]
