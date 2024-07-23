from djoser.serializers import UserCreateSerializer as BaseUserRegistrationSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from djoser.signals import user_activated
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string

from .models import *
from .signals import generate_otp
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import Permission, Group
from drf_extra_fields.fields import Base64ImageField
from rest_framework_simplejwt.tokens import RefreshToken


from config import settings
 
User = get_user_model()

        

class UserRegistrationSerializer(BaseUserRegistrationSerializer):
    
    class Meta(BaseUserRegistrationSerializer.Meta):
        fields = ['id', "first_name", "last_name", "email", "role","phone", "password", "is_active"]
        
    
class UserDeleteSerializer(serializers.Serializer):
    current_password = serializers.CharField(style={"input_type": "password"})

class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={"input_type": "password"}, write_only=True, required=False)
    image_url = serializers.ReadOnlyField()
    
    class Meta():
        model = User
        fields = ['id',"first_name", "last_name", "email", "is_active", "role", "is_superuser", "date_joined"]


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
    
class FirebaseSerializer(serializers.Serializer):
    fcm_token = serializers.CharField(max_length=5000)


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(max_length=700) 
    

class OTPVerifySerializer(serializers.Serializer):
    otp = serializers.CharField(max_length=6)
    
    
    def verify_otp(self, request):
        otp = self.validated_data['otp']
        
        if ActivationOtp.objects.filter(code=otp).exists():
            try:
                otp = ActivationOtp.objects.get(code=otp)
            except Exception:
                ActivationOtp.objects.filter(code=otp).delete()
                raise serializers.ValidationError(detail='Cannot verify otp. Please try later')
            
            if otp.is_valid():
                otp.user.is_active=True
                otp.user.save()
                
                all_otps = ActivationOtp.objects.filter(user=otp.user)
                all_otps.delete()
                user_activated.send(User, user=otp.user, request=request)

                user = otp.user
                refresh = RefreshToken.for_user(user)

                data = {
                    "message": "auth success",
                    "code": "200",
                    "id": user.id,
                    "email": user.email,
                    "role": user.role,
                    "access": str(refresh.access_token),
                    "refresh": str(refresh)

                }

                return data
                
            else:
                raise serializers.ValidationError(detail='OTP expired')

        else:
            raise serializers.ValidationError(detail='Invalid OTP')
    

class NewOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    
     
    def get_new_otp(self):
        try:
            user = User.objects.get(email=self.validated_data['email'], is_active=False)
        except User.DoesNotExist:
            raise serializers.ValidationError(detail='Please confirm that the email is correct and has not been verified')
        
        code = generate_otp(6)
        expiry_date = timezone.now() + timezone.timedelta(minutes=10)
        
        ActivationOtp.objects.create(code=code, user=user, expiry_date=expiry_date)
        ###send mail
        
        return {'message': 'Please check your email for OTP.'}
    





class TeamSerializer(serializers.ModelSerializer):


    class Meta:
        model = Teams
        fields = "__all__"


    def create(self, validated_data):
        team = Teams.objects.create(**validated_data)
        return team


class ScanCountSerializer(serializers.ModelSerializer):


    class Meta:
        model = ScanCount
        fields = "__all__"





class ImageSerializer(serializers.Serializer):

    image = serializers.ImageField()



class BinDataSerializer(serializers.Serializer):

    bin_color = serializers.CharField(max_length=100, required=True)
    color = serializers.CharField(max_length=100, required=True)
    
