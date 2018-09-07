# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-01-29 06:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agents', '0005_agentcategory_agentpagecategorychoice'),
    ]

    operations = [
        migrations.AddField(
            model_name='agentpage',
            name='email',
            field=models.EmailField(blank=True, default='', max_length=254),
        ),
        migrations.AddField(
            model_name='agentpage',
            name='phone',
            field=models.CharField(blank=True, default='', max_length=25),
        ),
    ]