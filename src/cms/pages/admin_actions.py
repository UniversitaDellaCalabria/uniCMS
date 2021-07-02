from django.http import HttpResponseRedirect
from django.shortcuts import render

from cms.contexts.models import *
from cms.pages.models import *
from cms.templates.models import *

from . forms import PageTemplatesListForm


def update_template(self, request, queryset):
    """
    update template to selected pages
    """
    if 'update_template' in request.POST:

        form = PageTemplatesListForm(data=request.POST)
        if form.is_valid():
            template = PageTemplate.objects.get(pk=form.data['template'])
            queryset.update(base_template=template)
            self.message_user(request,
                              "Changed template on {} pages"
                              "".format(queryset.count()))
            return HttpResponseRedirect(request.get_full_path())

    form = PageTemplatesListForm()
    return render(request,
                  'admin/update_template.html',
                  context={'opts': Page._meta,
                           'pages':queryset,
                           'form': form})

update_template.short_description = "Update template"
