# Generated by Django 3.1.4 on 2021-01-15 11:24

import cms.publications.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import taggit.managers

from cms.medias.settings import FILETYPE_ALLOWED
from cms.templates.models import CMS_TEMPLATE_BLOCK_SECTIONS

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cmstemplates', '0001_initial'),
        ('cmsmedias', '0001_initial'),
        ('cmscontexts', '0001_initial'),
        ('cmspages', '0001_initial'),
        ('taggit', '0003_taggeditem_add_unique_index'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField()),
                ('title', models.CharField(help_text='Heading, Headline', max_length=256)),
                ('subheading', models.TextField(blank=True, help_text='Strap line (press)', max_length=1024, null=True)),
                ('content', models.TextField(blank=True, help_text='Content', null=True)),
                ('content_type', models.CharField(choices=[('markdown', 'markdown'), ('html', 'html')], default='markdown', max_length=33)),
                ('state', models.CharField(choices=[('draft', 'Draft'), ('published', 'Published')], default='draft', max_length=33)),
                ('date_start', models.DateTimeField()),
                ('date_end', models.DateTimeField()),
                ('note', models.TextField(blank=True, help_text='Editorial Board notes', null=True)),
                ('slug', models.SlugField(blank=True, null=True)),
                ('relevance', models.IntegerField(blank=True, default=0)),
                ('category', models.ManyToManyField(to='cmspages.Category')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='publication_created_by', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='publication_modified_by', to=settings.AUTH_USER_MODEL)),
                ('presentation_image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cmsmedias.media')),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
            ],
            options={
                'verbose_name_plural': 'Publications',
            },
        ),
        migrations.CreateModel(
            name='PublicationLocalization',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField()),
                ('title', models.CharField(help_text='Heading, Headline', max_length=256)),
                ('language', models.CharField(choices=(lambda: settings.LANGUAGES)(), default='en', max_length=12)),
                ('subheading', models.TextField(blank=True, help_text='Strap line (press)', max_length=1024, null=True)),
                ('content', models.TextField(blank=True, help_text='Content', null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='publicationlocalization_created_by', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='publicationlocalization_modified_by', to=settings.AUTH_USER_MODEL)),
                ('publication', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cmspublications.publication')),
            ],
            options={
                'verbose_name_plural': 'Publication Localizations',
            },
        ),
        migrations.CreateModel(
            name='PublicationLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=256)),
                ('url', models.URLField(help_text='url')),
                ('publication', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cmspublications.publication')),
            ],
            options={
                'verbose_name_plural': 'Publication Links',
            },
        ),
        migrations.CreateModel(
            name='PublicationGallery',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('order', models.IntegerField(blank=True, default=10, null=True)),
                ('is_active', models.BooleanField()),
                ('collection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cmsmedias.mediacollection')),
                ('publication', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cmspublications.publication')),
            ],
            options={
                'verbose_name_plural': 'Publication Image Gallery',
            },
        ),
        migrations.CreateModel(
            name='PublicationContext',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('order', models.IntegerField(blank=True, default=10, null=True)),
                ('is_active', models.BooleanField()),
                ('section', models.CharField(blank=True, choices=(lambda: CMS_TEMPLATE_BLOCK_SECTIONS)(), 
                                             help_text='Specify the container section in the template where this block would be rendered.', max_length=60, null=True)),
                ('in_evidence_start', models.DateTimeField(blank=True, null=True)),
                ('in_evidence_end', models.DateTimeField(blank=True, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='publicationcontext_created_by', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='publicationcontext_modified_by', to=settings.AUTH_USER_MODEL)),
                ('publication', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cmspublications.publication')),
                ('webpath', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cmscontexts.webpath')),
            ],
            options={
                'verbose_name_plural': 'Publication Contexts',
            },
        ),
        migrations.CreateModel(
            name='PublicationBlock',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('order', models.IntegerField(blank=True, default=10, null=True)),
                ('is_active', models.BooleanField()),
                ('section', models.CharField(blank=True, choices=(lambda: CMS_TEMPLATE_BLOCK_SECTIONS)(), 
                             help_text='Specify the container section in the template where this block would be rendered.', max_length=60, null=True)),
                ('block', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cmstemplates.templateblock')),
                ('publication', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cmspublications.publication')),
            ],
            options={
                'verbose_name_plural': 'Publication Page Block',
            },
        ),
        migrations.CreateModel(
            name='PublicationAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('order', models.IntegerField(blank=True, default=10, null=True)),
                ('is_active', models.BooleanField()),
                ('file_size', models.IntegerField(blank=True, null=True)),
                ('file_type', models.CharField(blank=True, choices=(lambda: FILETYPE_ALLOWED)(), max_length=256, null=True)),
                ('name', models.CharField(blank=True, help_text='Specify the container section in the template where this block would be rendered.', max_length=60, null=True)),
                ('file', models.FileField(upload_to=cms.publications.models.publication_attachment_path)),
                ('description', models.TextField()),
                ('publication', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='page_attachment', to='cmspublications.publication')),
            ],
            options={
                'verbose_name_plural': 'Publication Attachments',
            },
        ),
        migrations.CreateModel(
            name='PublicationRelated',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('order', models.IntegerField(blank=True, default=10, null=True)),
                ('is_active', models.BooleanField()),
                ('publication', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parent_page', to='cmspublications.publication')),
                ('related', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_page', to='cmspublications.publication')),
            ],
            options={
                'verbose_name_plural': 'Related Publications',
                'unique_together': {('publication', 'related')},
            },
        ),
    ]
