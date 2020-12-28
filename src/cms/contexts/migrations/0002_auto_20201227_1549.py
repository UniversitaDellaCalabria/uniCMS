# Generated by Django 3.1.2 on 2020-12-27 15:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cmscontexts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='editorialboardeditors',
            name='permission',
            field=models.CharField(choices=[('1', 'edit created by them in their own context'), ('2', 'edit all pages in their own context'), ('3', 'edit all pages in their own context and descendants'), ('4', 'translate all pages in their own context'), ('5', 'translate all pages in their own context and descendants'), ('6', 'publish created by them in their own context'), ('7', 'publish all pages in their own context'), ('8', 'publish all pages in their own context and descendants')], max_length=5),
        ),
        migrations.AlterField(
            model_name='webpath',
            name='site',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cmscontexts.website'),
        ),
    ]