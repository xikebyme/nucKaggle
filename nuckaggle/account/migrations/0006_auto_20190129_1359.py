# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2019-01-29 05:59
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_auto_20190129_1353'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='team',
            options={'verbose_name_plural': '队伍'},
        ),
    ]