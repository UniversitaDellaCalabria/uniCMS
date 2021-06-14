# Generated by Django 3.2.3 on 2021-06-14 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmstemplates', '0005_auto_20210614_1032'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pagetemplate',
            name='template_file',
            field=models.CharField(choices=[('publication_view_hero_original.html', 'publication_view_hero_original.html'), ('unical_center_top_ab_a_double.html', 'unical_center_top_ab_a_double.html'), ('dipartimento_home_v3_dimes.html', 'dipartimento_home_v3_dimes.html'), ('publication_view.html', 'publication_view.html'), ('portale_home_dipartimento_v3.html', 'portale_home_dipartimento_v3.html'), ('unical_main_center_alternative.html', 'unical_main_center_alternative.html'), ('unical.html', 'unical.html'), ('portale_home_v_original.html', 'portale_home_v_original.html'), ('dipartimento_home_v3.html', 'dipartimento_home_v3.html'), ('unical_right_spaced.html', 'unical_right_spaced.html'), ('publication_list.html', 'publication_list.html'), ('portale_home_dipartimento_v3_dimes.html', 'portale_home_dipartimento_v3_dimes.html'), ('italia.html', 'italia.html')], max_length=1024),
        ),
    ]
