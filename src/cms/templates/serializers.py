from django.conf import settings

from cms.api.serializers import UniCMSCreateUpdateSerializer

from . models import *
from . import settings as app_settings


CMS_BLOCK_TYPES = getattr(settings, 'CMS_BLOCK_TYPES',
                          app_settings.CMS_BLOCK_TYPES)


class PageTemplateSerializer(UniCMSCreateUpdateSerializer):

    class Meta:
        model = PageTemplate
        fields = '__all__'


class TemplatesBlockSerializer(UniCMSCreateUpdateSerializer):
    CMS_BLOCK_TYPES
    def to_representation(self, instance):
        data = super().to_representation(instance)
        for t in CMS_BLOCK_TYPES:
            if t[0] == instance.type:
                data['type_friendly'] = t[1]
                break
        return data

    class Meta:
        model = TemplateBlock
        fields = '__all__'


class TemplateBlockSerializer(UniCMSCreateUpdateSerializer):

    block = TemplatesBlockSerializer()

    class Meta:
        model = PageTemplateBlock
        fields = '__all__'
