from django.urls import reverse

from cms.api.serializers import (UniCMSContentTypeClass,
                                 UniCMSCreateUpdateSerializer,
                                 UniCMSTagsValidator)
from cms.carousels.serializers import CarouselSerializer
from cms.contexts.models import WebPath
from cms.contexts.serializers import WebPathSerializer
from cms.medias.serializers import MediaSerializer, MediaCollectionSerializer
from cms.menus.serializers import MenuSerializer
from cms.publications.serializers import PublicationSerializer
from cms.templates.serializers import *

from rest_framework import serializers

from taggit_serializer.serializers import (TagListSerializerField,
                                           TaggitSerializer)

from . models import *


class PageForeignKey(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get('request', None)
        if request:
            page_id = self.context['request'].parser_context['kwargs']['page_id']
            return Page.objects.filter(pk=page_id)
        return None # pragma: no cover


class WebPathForeignKey(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get('request', None)
        if request:
            if request.method in ['PATCH','PUT']:
                return WebPath.objects.all()
            site_id = self.context['request'].parser_context['kwargs']['site_id']
            webpath_id = self.context['request'].parser_context['kwargs']['webpath_id']
            return WebPath.objects.filter(pk=webpath_id,
                                          site__id=site_id)
        return None # pragma: no cover


class PageSerializer(TaggitSerializer,
                     UniCMSCreateUpdateSerializer,
                     UniCMSContentTypeClass,
                     UniCMSTagsValidator):
    webpath = WebPathForeignKey()
    tags = TagListSerializerField()

    def to_internal_value(self, data):
        if data.get('date_end') == '':
            data['date_end'] = None # pragma: no cover
        return super().to_internal_value(data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        base_template = PageTemplateSerializer(instance.base_template)
        webpath = WebPathSerializer(instance.webpath)
        preview_url = reverse('unicms:page-preview',
                              kwargs={'page_id': data['id']})
        data['base_template'] = base_template.data
        data['webpath'] = webpath.data
        data['preview_url'] = preview_url
        return data

    class Meta:
        model = Page
        fields = '__all__'
        read_only_fields = ('is_active', 'created_by',
                            'modified_by', 'state')


class PageBlockSerializer(UniCMSContentTypeClass):
    page = PageForeignKey()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        block = TemplatesBlockSerializer(instance.block)
        data['block'] = block.data
        return data

    class Meta:
        model = PageBlock
        fields = '__all__'


class PageCarouselSerializer(UniCMSContentTypeClass):
    page = PageForeignKey()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        carousel = CarouselSerializer(instance.carousel)
        data['carousel'] = carousel.data
        return data

    class Meta:
        model = PageCarousel
        fields = '__all__'


class PageLinkSerializer(UniCMSContentTypeClass):
    page = PageForeignKey()

    class Meta:
        model = PageLink
        fields = '__all__'


class PageLocalizationSerializer(UniCMSCreateUpdateSerializer,
                                 UniCMSContentTypeClass):
    page = PageForeignKey()

    class Meta:
        model = PageLocalization
        fields = '__all__'
        read_only_fields = ('created_by', 'modified_by')


class PageMenuSerializer(UniCMSCreateUpdateSerializer,
                         UniCMSContentTypeClass):
    page = PageForeignKey()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        menu = MenuSerializer(instance.menu)
        data['menu'] = menu.data
        return data

    class Meta:
        model = PageMenu
        fields = '__all__'


class PageMediaCollectionSerializer(UniCMSCreateUpdateSerializer,
                                    UniCMSContentTypeClass):
    page = PageForeignKey()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        collection = MediaCollectionSerializer(instance.collection)
        data['collection'] = collection.data
        return data

    class Meta:
        model = PageMediaCollection
        fields = '__all__'


class PageMediaSerializer(UniCMSCreateUpdateSerializer,
                          UniCMSContentTypeClass):
    page = PageForeignKey()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        media = MediaSerializer(instance.media)
        data['media'] = media.data
        return data

    class Meta:
        model = PageMedia
        fields = '__all__'


class PagePublicationSerializer(UniCMSCreateUpdateSerializer,
                                UniCMSContentTypeClass):
    page = PageForeignKey()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        publication = PublicationSerializer(instance.publication)
        data['publication'] = publication.data
        return data

    class Meta:
        model = PagePublication
        fields = '__all__'


class PageRelatedSerializer(UniCMSCreateUpdateSerializer,
                            UniCMSContentTypeClass):
    page = PageForeignKey()

    def to_representation(self, instance):
        data = super().to_representation(instance)
        related_page = PageSerializer(instance.related_page)
        data['related_page'] = related_page.data
        return data

    class Meta:
        model = PageRelated
        fields = '__all__'


class PageHeadingSerializer(UniCMSContentTypeClass):
    page = PageForeignKey()

    class Meta:
        model = PageHeading
        fields = '__all__'


class HeadingForeignKey(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get('request', None)
        if request:
            page_id = self.context['request'].parser_context['kwargs']['page_id']
            heading_id = self.context['request'].parser_context['kwargs']['heading_id']
            return PageHeading.objects.filter(pk=heading_id,
                                              page__pk=page_id)
        return None # pragma: no cover


class PageHeadingLocalizationSerializer(UniCMSContentTypeClass):
    heading = HeadingForeignKey()

    class Meta:
        model = PageHeadingLocalization
        fields = '__all__'
