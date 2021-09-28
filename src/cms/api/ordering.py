from django.core.exceptions import FieldError
from rest_framework.filters import OrderingFilter


# Work around DRF issue #6886 by always adding the primary key as last order field.
class StableOrderingFilter(OrderingFilter):
    def get_ordering(self, request, queryset, view):
        ordering = super(StableOrderingFilter, self).get_ordering(request, queryset, view)
        pk = queryset.model._meta.pk.name
        if ordering is None: return [pk,]
        for field in queryset.model._meta.fields:
            if field.__dict__['name'] == 'order':
                return list(ordering) + ['order', pk,]
        return list(ordering) + [pk,]
