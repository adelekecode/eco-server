from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.utils import timezone
from django.core.validators import MinLengthValidator, FileExtensionValidator
from django.forms import model_to_dict
from django.utils.text import slugify
from .managers import UserManager
import uuid
import random







class User(AbstractBaseUser, PermissionsMixin):
    
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )   
    
        
    id = models.UUIDField(primary_key=True, unique=True, editable=False, default=uuid.uuid4)
    first_name    = models.CharField(_('first name'),max_length = 250)
    last_name     = models.CharField(_('last name'),max_length = 250)
    role          = models.CharField(_('role'), max_length = 255, choices=ROLE_CHOICES)
    email         = models.EmailField(_('email'), unique=True)
    image = models.ImageField(
        upload_to='profile_photos/', 
        validators=[
            FileExtensionValidator(
                allowed_extensions=['png', "jpg", "jpeg"])
        ], 
        blank=True, null=True)
    password      = models.CharField(_('password'), max_length=300)
    is_staff      = models.BooleanField(_('staff'), default=False)
    is_admin      = models.BooleanField(_('admin'), default= False)
    is_active     = models.BooleanField(_('active'), default=True)
    is_deleted    = models.BooleanField(_('deleted'), default=False)
    date_joined   = models.DateTimeField(_('date joined'), auto_now_add=True)
    fcm_token = models.TextField(null=True)
    points = models.IntegerField(default=0)
    teams = models.IntegerField(default=0)
    provider = models.CharField(_('provider'), max_length=255, default="email", choices=(('email',"email"),
                                                                                         ('google',"google")))
    
    

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['id','first_name', 'last_name', 'role', 'phone', ]
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return f"{self.email} -- {self.role}"
    
    
    
    @property
    def image_url(self):
        
        """See the image url of the user

        Returns:
            str: Image url of the  user or empty string if no image uploaded
        """
        
        if self.image:
            return self.image.url
        return ""
    
    def delete(self):
        
        """
        Performs soft delete on the user model
        Delete the user by flagging it as deleted and adding updating the email and phone with delete flags.
        """
        
        self.is_deleted = True
        self.email = f"{random.randint(0,100000)}-deleted-{self.email}"
        self.phone = f"{self.phone}-deleted-{random.randint(0,100000)}"
        self.save()
        
        return 
        
    def delete_permanently(self):
        
        """
        Performs hard delete on the user model.
        To be used with caution!
        """
        
        super().delete()
        
        return 
        
        
    class Meta:
        """additional permission to the  user model for viewing dashboards"""
        permissions = [
            ("view_dashboard", "Can view all dashboards"),
        ]
        
    
    
        
        
class ActivationOtp(models.Model):
    """
    Database schema for Activation Otp model.

    Fields:
        - id (int): Unique identifier for the OTP.
        - code (str): OTP for the user
        - user (FK): User attached to the  otp
        - expiry_date (datetime): Time at which the OTP expires.
    """

    user  =models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    expiry_date = models.DateTimeField()
    
    
    def is_valid(self):
        """Checks if the OTP has expires or not

        Returns:
            bool: Result of OTP check.
        """
        
        return bool(self.expiry_date > timezone.now())



class ActivityLog(models.Model):
    """
    Database schema for user activity logs.

    Fields:
        - user (FK): User that the log belongs to
        - action (str): action performed by user
        - date_created (timestamp): date the log was created
        - is_deleted (bool): flags the log as deleted
    
    """
    
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    
    
    def delete(self):
        self.is_deleted = True
        self.save()
        
        
    def delete_permanently(self):
        super().delete()
        
        
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} -- {self.action}"
    


class Teams(models.Model):

    id = models.UUIDField(primary_key=True, unique=True, editable=False, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    key = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True)
    users = models.ManyToManyField(User, related_name="team_users", blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


    




class ScanCount(models.Model):

    id = models.UUIDField(primary_key=True, unique=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    team = models.ForeignKey(Teams, on_delete=models.CASCADE, null=True)

    count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)


    