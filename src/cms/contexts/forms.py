from django import forms
from django.contrib.auth import get_user_model
from django.forms import ModelForm
from django.urls import reverse

from cms.api.settings import FORM_SOURCE_LABEL
from cms.publications.models import PublicationContext

from . models import EditorialBoardLockUser, WebPath, WebSite


class EditorialBoardLockUserForm(forms.Form):

    user = forms.ModelChoiceField(queryset=get_user_model().objects.filter(is_staff=True))


class WebPathForm(ModelForm):

    def __init__(self, *args, **kwargs):
        site_id = kwargs.pop('site_id', None)
        super().__init__(*args, **kwargs)
        if site_id:
            self.fields['site'].queryset = WebSite.objects.filter(pk=site_id)
            self.fields['parent'].queryset = WebPath.objects.filter(site__pk=site_id)
            setattr(self.fields['parent'],
                    FORM_SOURCE_LABEL,
                    reverse('unicms_api:webpath-options',
                            kwargs={'site_id': site_id}))
            setattr(self.fields['alias'],
                    FORM_SOURCE_LABEL,
                    reverse('unicms_api:webpath-options',
                            kwargs={'site_id': site_id}))

    class Meta:
        model = WebPath
        fields = ['site', 'name', 'parent',
                  'alias', 'alias_url', 'path', 'is_active']


class PublicationContextForm(ModelForm):

    def __init__(self, *args, **kwargs):
        site_id = kwargs.pop('site_id', None)
        webpath_id = kwargs.pop('webpath_id', None)
        super().__init__(*args, **kwargs)
        if site_id:
            if webpath_id:
                self.fields['webpath'].queryset = WebPath.objects.filter(pk=webpath_id,
                                                                         site__pk=site_id)
            else:
                self.fields['webpath'].queryset = WebPath.objects.filter(site__pk=site_id)
            setattr(self.fields['webpath'],
                    FORM_SOURCE_LABEL,
                    reverse('unicms_api:webpath-options',
                            kwargs={'site_id': site_id}))
        setattr(self.fields['publication'],
                FORM_SOURCE_LABEL,
                reverse('unicms_api:editorial-board-publications-options'))

    class Meta:
        model = PublicationContext
        fields = ['webpath', 'publication',
                  'date_start', 'date_end',
                  'in_evidence_start', 'in_evidence_end',
                  'order', 'is_active']
