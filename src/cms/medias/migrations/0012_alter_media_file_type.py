# Generated by Django 3.2.19 on 2023-08-23 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmsmedias', '0011_alter_media_uuid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='file_type',
            field=models.CharField(blank=True, choices=[('', '')], max_length=256, null=True),
        ),
    ]
