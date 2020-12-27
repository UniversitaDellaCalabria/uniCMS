# Generated by Django 3.1.2 on 2020-12-27 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmstemplates', '0005_auto_20201218_1224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pagetemplate',
            name='template_file',
            field=models.CharField(choices=[('dipartimento_home_v3_dimes.html', 'dipartimento_home_v3_dimes.html'), ('unical_main_center_alternative.html', 'unical_main_center_alternative.html'), ('publication_list.html', 'publication_list.html'), ('publication_view_hero_original.html', 'publication_view_hero_original.html'), ('italia.html', 'italia.html'), ('publication_view.html', 'publication_view.html'), ('portale_home_dipartimento_v3.html', 'portale_home_dipartimento_v3.html'), ('portale_home_v_original.html', 'portale_home_v_original.html'), ('portale_home_dipartimento_v3_dimes.html', 'portale_home_dipartimento_v3_dimes.html'), ('unical_main_spaced_columns.html', 'unical_main_spaced_columns.html'), ('unical_main.html', 'unical_main.html'), ('dipartimento_home_v3.html', 'dipartimento_home_v3.html')], max_length=1024),
        ),
        migrations.AlterField(
            model_name='pagetemplateblock',
            name='section',
            field=models.CharField(blank=True, choices=[('pre-head', 'Pre-Header'), ('head', 'Header'), ('menu-1', 'Navigation Main Menu'), ('menu-2', 'Navigation Menu 2'), ('menu-3', 'Navigation Menu 3'), ('menu-4', 'Navigation Menu 4'), ('banner', 'Banner/Slider'), ('slider-2', 'Carousel/Slider 2'), ('pre-footer', 'Pre-Footer'), ('footer', 'Footer'), ('post-footer', 'Post-Footer'), ('breadcrumbs', 'Breadcrumbs'), ('section-1', (('1-top-a', 'Section 1 - Top A'), ('1-top-b', 'Section 1 - Top B'), ('1-top-c', 'Section 1 - Top C'), ('1-mid-top-a', 'Section 1 - Middle Top A'), ('1-mid-top-b', 'Section 1 - Middle Top B'), ('1-mid-top-c', 'Section 1 - Middle Top C'), ('1-left-a', 'Section 1 - Left A'), ('1-left-b', 'Section 1 - Left B'), ('1-center-top-a', 'Section 1 - Center Top A'), ('1-center-top-b', 'Section 1 - Center Top B'), ('1-center-top-c', 'Section 1 - Center Top C'), ('1-center-content', 'Section 1 - Center Content'), ('1-center-bottom-a', 'Section 1 - Center Bottom A'), ('1-center-bottom-b', 'Section 1 - Center Bottom B'), ('1-center-bottom-c', 'Section 1 - Center Bottom C'), ('1-right-a', 'Section 1 - Right A'), ('1-right-b', 'Section 1 - Right B'), ('1-mid-bottom-a', 'Section 1 - Middle Bottom A'), ('1-mid-bottom-b', 'Section 1 - Middle Bottom B'), ('1-mid-bottom-c', 'Section 1 - Middle Bottom C'), ('1-bottom-a', 'Section 1 - Bottom A'), ('1-bottom-b', 'Section 1 - Bottom B'), ('1-bottom-c', 'Section 1 - Bottom C'))), ('section-2', (('2-top-a', 'Section 2 - Top A'), ('2-top-b', 'Section 2 - Top B'), ('2-top-c', 'Section 2 - Top C'), ('2-mid-top-a', 'Section 2 - Middle Top A'), ('2-mid-top-b', 'Section 2 - Middle Top B'), ('2-mid-top-c', 'Section 2 - Middle Top C'), ('2-left-a', 'Section 2 - Left A'), ('2-left-b', 'Section 2 - Left B'), ('2-center-top-a', 'Section 2 - Center Top A'), ('2-center-top-b', 'Section 2 - Center Top B'), ('2-center-top-c', 'Section 2 - Center Top C'), ('2-center-content', 'Section 2 - Center Content'), ('2-center-bottom-a', 'Section 2 - Center Bottom A'), ('2-center-bottom-b', 'Section 2 - Center Bottom B'), ('2-center-bottom-c', 'Section 2 - Center Bottom C'), ('2-right-a', 'Section 2 - Right A'), ('2-right-b', 'Section 2 - Right B'), ('2-mid-bottom-a', 'Section 2 - Middle Bottom A'), ('2-mid-bottom-b', 'Section 2 - Middle Bottom B'), ('2-mid-bottom-c', 'Section 2 - Middle Bottom C'), ('2-bottom-a', 'Section 2 - Bottom A'), ('2-bottom-b', 'Section 2 - Bottom B'), ('2-bottom-c', 'Section 2 - Bottom C'))), ('section-3', (('3-top-a', 'Section 3 - Top A'), ('3-top-b', 'Section 3 - Top B'), ('3-top-c', 'Section 3 - Top C'), ('3-mid-top-a', 'Section 3 - Middle Top A'), ('3-mid-top-b', 'Section 3 - Middle Top B'), ('3-mid-top-c', 'Section 3 - Middle Top C'), ('3-left-a', 'Section 3 - Left A'), ('3-left-b', 'Section 3 - Left B'), ('3-center-top-a', 'Section 3 - Center Top 1'), ('3-center-top-b', 'Section 3 - Center Top 2'), ('3-center-top-c', 'Section 3 - Center Top 3'), ('3-center-content', 'Section 3 - Center Content'), ('3-center-bottom-a', 'Section 3 - Center Bottom A'), ('3-center-bottom-b', 'Section 3 - Center Bottom B'), ('3-center-bottom-c', 'Section 3 - Center Bottom C'), ('3-mid-bottom-a', 'Section 3 - Middle Bottom A'), ('3-mid-bottom-b', 'Section 3 - Middle Bottom B'), ('3-mid-bottom-c', 'Section 3 - Middle Bottom C'), ('3-bottom-a', 'Section 3 - Bottom A'), ('3-bottom-b', 'Section 3 - Bottom B'), ('3-bottom-c', 'Section 3 - Bottom C')))], help_text='Specify the container section in the template where this block would be rendered.', max_length=33, null=True),
        ),
        migrations.AlterField(
            model_name='templateblock',
            name='type',
            field=models.TextField(choices=[('cms.templates.blocks.HtmlBlock', 'HTML Block'), ('cms.templates.blocks.JSONBlock', 'JSON Block'), ('cms.templates.blocks.LinkPlaceholderBlock', 'Link Placeholder Block'), ('cms.templates.blocks.PublicationContentPlaceholderBlock', 'Publication Content Placeholder Block')]),
        ),
    ]
