# Generated by Django 3.1.6 on 2021-05-07 20:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cmsmedias', '0005_auto_20210507_1618'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='media',
            name='is_active',
        ),
    ]