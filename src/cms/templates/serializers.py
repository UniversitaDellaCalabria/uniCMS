from cms.api.serializers import UniCMSCreateUpdateSerializer


from . models import *


class PageTemplateSerializer(UniCMSCreateUpdateSerializer):

    class Meta:
        model = PageTemplate
        fields = '__all__'


class TemplatesBlockSerializer(UniCMSCreateUpdateSerializer):

    class Meta:
        model = TemplateBlock
        fields = '__all__'


class TemplateBlockSerializer(UniCMSCreateUpdateSerializer):

    block = TemplatesBlockSerializer()

    class Meta:
        model = PageTemplateBlock
        fields = '__all__'
