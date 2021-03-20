from cms.api.serializers import UniCMSCreateUpdateSerializer


from . models import *


class PageTemplateSerializer(UniCMSCreateUpdateSerializer):

    class Meta:
        model = PageTemplate
        fields = '__all__'


class TemplateBlockSerializer(UniCMSCreateUpdateSerializer):

    class Meta:
        model = TemplateBlock
        fields = '__all__'
