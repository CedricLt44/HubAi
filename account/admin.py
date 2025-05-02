from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class UserAdmin(BaseUserAdmin):
    # Champs affichés dans la liste des utilisateurs
    list_display = ('email', 'name', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    
    # Champs pour l'édition dans l'admin
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations personnelles', {'fields': ('name',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates importantes', {'fields': ('last_login',)}),
    )

    # Champs pour la création d’un nouvel utilisateur via l’admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2', 'is_staff', 'is_superuser'),
        }),
    )

    search_fields = ('email', 'name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

# Enregistrement du modèle User avec sa configuration personnalisée
admin.site.register(User, UserAdmin)