from rest_framework_simplejwt.token_blacklist import models, admin
from django.contrib.admin import AdminSite

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
    
    
admin.site.unregister(models.OutstandingToken)
admin.site.register(models.OutstandingToken, CustomOutstandingTokenAdmin)

