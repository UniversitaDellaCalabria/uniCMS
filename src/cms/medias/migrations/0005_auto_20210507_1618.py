# Generated by Django 3.1.6 on 2021-05-07 16:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cmsmedias', '0004_auto_20210415_1304'),
    ]

    operations = [
        migrations.AlterField(
            model_name='media',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='media_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='media',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='media_modified_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='mediacollection',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mediacollection_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='mediacollection',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mediacollection_modified_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='mediacollectionitem',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mediacollectionitem_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='mediacollectionitem',
            name='media',
            field=models.ForeignKey(limit_choices_to={'is_active': True}, on_delete=django.db.models.deletion.PROTECT, to='cmsmedias.media'),
        ),
        migrations.AlterField(
            model_name='mediacollectionitem',
            name='modified_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mediacollectionitem_modified_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
