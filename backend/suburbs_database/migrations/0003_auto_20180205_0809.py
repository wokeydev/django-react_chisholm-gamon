# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-02-05 08:09
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('suburbs_database', '0002_auto_20180204_2053'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='suburbdata',
            options={'ordering': ['name']},
        ),
    ]