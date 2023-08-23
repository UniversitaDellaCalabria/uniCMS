# Generated by Django 3.2.19 on 2023-08-23 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmscontacts', '0005_alter_contactinfo_info_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactinfolocalization',
            name='language',
            field=models.CharField(choices=[('', '-')], default='en', max_length=12),
        ),
        migrations.AlterField(
            model_name='contactlocalization',
            name='language',
            field=models.CharField(choices=[('', '-')], default='en', max_length=12),
        ),
    ]
