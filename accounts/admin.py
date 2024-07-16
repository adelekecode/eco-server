from typing import Any
from django.db.models.query import QuerySet
from django.http import HttpRequest
from rest_framework_simplejwt.token_blacklist import models, admin
from django.contrib.admin import AdminSite
from .models import ScanCount, Teams

class CustomOutstandingTokenAdmin(admin.OutstandingTokenAdmin):
    
    def has_delete_permission(self, *args, **kwargs):
        return True # or whatever logic you want

from django.contrib import admin
from django.contrib.auth.models import Permission

from django.contrib.auth import get_user_model

User = get_user_model()

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "teams", "points", "date_joined", "is_active"]
    list_editable = ["is_active"]
    search_fields = ["email"]
    # list_filter = ["is_active", "role"]
    ordering = ["email"]

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_deleted=False, role='user')

class TeamsAdmin(admin.ModelAdmin):
    list_display = ["name", "owner", "owners", "key", "description", "created_at", "updated_at"]


    def owner(self, obj):

        return obj.user.email
    
    owner.short_description = "Owner's Email"

    def owners(self, obj):
        return obj.users.all().count() if obj.users else 0
    
    owners.short_description = "Number of Users"    
    
admin.site.unregister(models.OutstandingToken)
admin.site.register(models.OutstandingToken, CustomOutstandingTokenAdmin)

admin.site.register(Teams, TeamsAdmin)

