# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-02-27 09:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0002_auto_20170928_0209'),
    ]

    operations = [
        migrations.AlterField(
            model_name='skills',
            name='skill',
            field=models.CharField(default='', max_length=25),
        ),
    ]
