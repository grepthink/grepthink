# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-10-18 04:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tsr',
            name='late',
            field=models.BooleanField(default=False),
        ),
    ]
