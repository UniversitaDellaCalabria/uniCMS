from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.admin import UserAdmin

from .models import *

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    readonly_fields = ('date_joined', 'last_login',)
    list_display = ('username', 'first_name', 'last_name',
                    'email', 'is_active', 'last_login',
                    'is_staff', 'is_superuser', )
    list_filter = ('date_joined',)
    list_editable = ('is_active', 'is_staff', 'is_superuser',)
    fieldsets = (
        (None, {'fields': (('username', 'is_active', 'is_staff', 'is_superuser', ),
                           ('password'),
                           )
                }),
        (_('Anagrafica'), {'fields': (('first_name', 'last_name'),
                                          'email',
                                         ('taxpayer_id',),
                                         ('matricola_studente',
                                          'matricola_dipendente',),
                                        )
                          }),

        (_('Permissions'), {'fields': ('groups', 'user_permissions'),
                            'classes':('collapse',)
                            }),


        (_('Date accessi sistema'), {'fields': (('date_joined',
                                                 'last_login', ))
                                    }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
