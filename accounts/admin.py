from rest_framework_simplejwt.token_blacklist import models, admin
from django.contrib.admin import AdminSite
from .models import ScanCount, Teams

class CustomOutstandingTokenAdmin(admin.OutstandingTokenAdmin):
    
    def has_delete_permission(self, *args, **kwargs):
        return True # or whatever logic you want

from django.contrib import admin
from accounts.models import User, ActivationOtp
from django.contrib.auth.models import Permission

# Register your models here.
    
    
@admin.register(User)
class Users(admin.ModelAdmin):
    list_display = ["email", "role", "is_active", ]
    list_editable = ["is_active"]


class TeamsAdmin(admin.ModelAdmin):
    list_display = ["name", "owner", "users", "key", "description", "created_at", "updated_at"]


    def owner(self, obj):

        return obj.user.email
    
    owner.short_description = "Owner's Email"

    def users(self, obj):
        return obj.users.all().count()
    
    users.short_description = "Number of Users"    
    
admin.site.unregister(models.OutstandingToken)
admin.site.register(models.OutstandingToken, CustomOutstandingTokenAdmin)

admin.site.register(Teams, TeamsAdmin)

