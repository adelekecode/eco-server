from accounts.permissions import *
from .serializers import *
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg.utils import swagger_auto_schema
from django.contrib.auth import get_user_model
from .helpers.generators import generate_password
from rest_framework.exceptions import *
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, logout
from django.contrib.auth.signals import user_logged_in, user_logged_out
from rest_framework.decorators import action
from djoser.views import UserViewSet
from .emails import *
from rest_framework.views import APIView
from django.contrib.auth.hashers import check_password
from django.db.models import Q
import random
from django.utils.text import slugify
import string
import requests
import os



 
User = get_user_model()




def gen_key(n):
    
    alphabet = string.ascii_letters
    code = ''.join(random.choice(alphabet) for i in range(n))
    return code



class CustomUserViewSet(UserViewSet):
    queryset = User.objects.filter(is_deleted=False)
    authentication_classes = [JWTAuthentication]
    
    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(role="user")

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_Response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    
    


@swagger_auto_schema(method='post', request_body=LoginSerializer())
@api_view([ 'POST'])
def user_auth(request):
    
    """Allows users to log in to the platform. Sends the jwt refresh and access tokens. Check settings for token life time."""
    
    if request.method == "POST":
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            email = data['email']
            if User.objects.filter(email=email).exists():

                code = generate_otp(6)
                user = User.objects.get(email=email)
                expiry_date = timezone.now() + timezone.timedelta(minutes=10)
                ActivationOtp.objects.create(code=code, user=user, expiry_date=expiry_date)

                mail = auth_otp(email=user.email, otp=code)
                print(mail)

                return Response({"message": "authentication successfull", "code": code}, status=200)

            else:
                user = User.objects.create(
                    email=email,
                    role="user"
                )

                code = ActivationOtp.objects.filter(user=user).first()
            
                return Response({"message": "authentication successfull", "code": code.code}, status=200)
            
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    else:
        return Response({"message": "method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
    





                

               
            
@swagger_auto_schema(method="post",request_body=LogoutSerializer())
@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """Log out a user by blacklisting their refresh token then making use of django's internal logout function to flush out their session and completely log them out.

    Returns:
        Json response with message of success and status code of 204.
    """
    
    serializer = LogoutSerializer(data=request.data)
    
    serializer.is_valid(raise_exception=True)
    
    try:
        token = RefreshToken(token=serializer.validated_data["refresh_token"])
        token.blacklist()
        user=request.user
        user_logged_out.send(sender=user.__class__,
                                        request=request, user=user)
        logout(request)
        
        return Response({"message": "success"}, status=status.HTTP_204_NO_CONTENT)
    except TokenError:
        return Response({"message": "failed", "error": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method="patch",request_body=FirebaseSerializer())
@api_view(["PATCH"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_firebase_token(request):
    """Update the FCM token for a logged in use to enable push notifications

    Returns:
        Json response with message of success and status code of 200.
    """
    
    serializer = FirebaseSerializer(data=request.data)
    
    serializer.is_valid(raise_exception=True)
    
    fcm_token = serializer.validated_data.get("fcm_token")

    request.user.fcm_token = fcm_token
    request.user.save()
        
    return Response({"message": "success"}, status=status.HTTP_200_OK)
    



@swagger_auto_schema(methods=['POST'],  request_body=NewOtpSerializer())
@api_view(['POST'])
def reset_otp(request):
    if request.method == 'POST':
        serializer = NewOtpSerializer(data = request.data)
        if serializer.is_valid():
            data = serializer.get_new_otp()
            
            return Response(data, status=status.HTTP_200_OK)
        
        else:
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        
        
            
@swagger_auto_schema(methods=['POST'], request_body=OTPVerifySerializer())
@api_view(['POST'])
def otp_verification(request):
    
    """Api view for verifying OTPs """

    if request.method == 'POST':

        serializer = OTPVerifySerializer(data = request.data)

        if serializer.is_valid():
            data = serializer.verify_otp(request)
            
            return Response(data, status=status.HTTP_200_OK)
        else:

            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(methods=['POST'], request_body=TeamSerializer())
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def teams_view(request):
    if request.method == 'POST':
        serializer = TeamSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        name = serializer.validated_data['name']
        slug = slugify(name)

        if Teams.objects.filter(slug=slug).exists():
            return Response({"error": "team with this name already exists"}, status=400)


        if not request.user.teams >= 2:


            serializer.validated_data['key'] = gen_key(4)
            serializer.validated_data['user'] = request.user
            team = serializer.create(serializer.validated_data)

            team.users.set([request.user])
            team.save()
            request.user.teams += 1
            request.user.save()
            

            return Response({"message": "success"}, status=200)
        else:
            return Response({"error": "you can't be in more than two teams"}, status=400)
 

@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def user_teams(self, request):
    if request.method == 'GET':

        teams = Teams.objects.filter(users__id=request.user.id, is_deleted=False)

        serializer = TeamSerializer(teams, many=True)
        return Response(serializer.data)
    

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def join_team(self, request):
    if request.method == 'POST':

        key = request.GET.get('key', None)
        if key is None:
            return Response({"error": "key is required"}, status=400)
        
        if request.user.team >= 2:
            return Response({"error": "you can't join more than two teams"}, status=400)

        
        team = Teams.objects.filter(key=key, is_deleted=False).first()
        if team is None:
            return Response({"error": "invalid key"}, status=400)
        
        if team.users.filter(id=request.user.id).exists():
            return Response({"error": "you're already a member of this team"}, status=400)
        
        if team.users.count() >= 10:
            return Response({"error": "team is full"}, status=400)
        
        team.users.add(request.user)
        team.save()
        
        return Response({"message": "success"}, status=200)