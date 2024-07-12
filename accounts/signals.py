import random
from django.dispatch import receiver
from django.core.mail import send_mail
from django.db.models.signals import post_save, pre_save
from django.contrib.auth import get_user_model
from config import settings
from djoser.signals import user_registered, user_activated
from .models import ActivationOtp
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
import json
import os
import  requests
from .emails import auth_otp

User = get_user_model()
site_name = ""


def generate_otp(n):
    return "".join([str(random.choice(range(10))) for _ in range(n)])



    



@receiver(post_save, sender=User)
def auth_mail_signal(sender, instance, created, **kwargs):

    if created:
        if not instance.role == "admin":

            code = generate_otp(6)
            expiry_date = timezone.now() + timezone.timedelta(minutes=10)

            ActivationOtp.objects.create(code=code, user=instance, expiry_date=expiry_date)

            auth_otp(email=instance.email, otp=code)
            
            return 
        
        return
