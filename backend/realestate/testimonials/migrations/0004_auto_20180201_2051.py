# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-02-01 20:51
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0040_page_draft_title'),
        ('testimonials', '0003_auto_20180126_0825'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='testimonial',
            name='id',
        ),
        migrations.AddField(
            model_name='testimonial',
            name='canonical',
            field=models.URLField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='testimonial',
            name='meta_description',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='testimonial',
            name='meta_keywords',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='testimonial',
            name='meta_title',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='testimonial',
            name='og_description',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='testimonial',
            name='og_img',
            field=models.URLField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='testimonial',
            name='og_title',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='testimonial',
            name='og_type',
            field=models.CharField(blank=True, default='', max_length=50),
        ),
        migrations.AddField(
            model_name='testimonial',
            name='og_url',
            field=models.URLField(blank=True, default=''),
        ),
        # migrations.AddField(
        #     model_name='testimonial',
        #     name='page_ptr',
        #     field=models.OneToOneField(auto_created=True, default=1, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page'),
        #     preserve_default=False,
        # ),
        migrations.AddField(
            model_name='testimonial',
            name='template_override',
            field=models.CharField(blank=True, default='', help_text='Load this specific page template', max_length=255),
        ),
        migrations.AddField(
            model_name='testimonial',
            name='title_tag',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
        migrations.AddField(
            model_name='testimonial',
            name='twitter_card',
            field=models.CharField(blank=True, default='', help_text='Type of Twitter card', max_length=50),
        ),
        migrations.AddField(
            model_name='testimonial',
            name='twitter_creator',
            field=models.CharField(blank=True, default='', help_text='@name of author', max_length=50),
        ),
        migrations.AddField(
            model_name='testimonial',
            name='twitter_description',
            field=models.CharField(blank=True, default='', max_length=200),
        ),
        migrations.AddField(
            model_name='testimonial',
            name='twitter_image',
            field=models.CharField(blank=True, default='', help_text='Images must be at least 120x120px', max_length=255),
        ),
        migrations.AddField(
            model_name='testimonial',
            name='twitter_site',
            field=models.CharField(blank=True, default='', help_text='@name of publisher', max_length=50),
        ),
        migrations.AddField(
            model_name='testimonial',
            name='twitter_title',
            field=models.CharField(blank=True, default='', max_length=255),
        ),
    ]