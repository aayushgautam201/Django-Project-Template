from django.shortcuts import render
from urllib.parse import urljoin
import requests
from django.urls import reverse


from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.http import JsonResponse
import jwt
from coreapp.settings import SECRET_KEY
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ObjectDoesNotExist
from user.email_utils import send_dynamic_email
from utility.response import api_response


from .models import User
from .serializers import *


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class UserCreationView(APIView):

    def post(self, request, format=None):
        serializer = UserCreationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            token = get_tokens_for_user(user)
            return Response(data={'token':token,
             'msg':'User Created Successfully'},
             status=status.HTTP_201_CREATED)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        if User.objects.filter(email=request.data.get('email')).exists():
            if serializer.is_valid(raise_exception=True):
                email = serializer.data.get('email')
                password = serializer.data.get('password')
                if email is None or password is None:
                    return Response(data={'No email or password!!!'},
                                    status=status.HTTP_400_BAD_REQUEST)
                user = authenticate(email=email, password=password)
                if user is not None:
                    token = get_tokens_for_user(user)
                    return Response(data={'token':token,
                                          'id':user.id,
                                            'is_admin':user.is_admin,
                                            'is_verified':user.is_verified,
                                    'status':'success',
                                    }, 
                                    status=status.HTTP_200_OK)
                else:
                    return Response(data={
                    'Email or Password is not valid'},
                    status=status.HTTP_400_BAD_REQUEST)
            return Response(data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(data={"Email doesnot exists"},
            status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    # pagination_classes = CustomPagination

    def get(self, request, format=None):
        serializer = UserProfileSerializer(request.user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data,context={'user':request.user})
        if serializer.is_valid(raise_exception=True):
            return Response(data={'password changed successfully'},
            status=status.HTTP_200_OK)
        else:
            print(serializer.errors)


# class ResetPasswordEmailView(APIView):
#     def post(self, request, format=None):
#         serializer = SendResetPasswordEmail(data=request.data)
#         if serializer.is_valid(raise_exception=True):
#             return Response(
#                 data={'reset password sent to the email, please check your email'},
#                 status=status.HTTP_200_OK)
#         return Response (serializer.errors,
#             status = status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    def post(self, request, uid, token, format=None):
        serializer = UserPasswordResetSerializer(data=request.data, context={'uid':uid, 'token':token})
        if serializer.is_valid(raise_exception=True):
            return Response(
                data={'password reset successful'},
                status=status.HTTP_200_OK)
        return Response (serializer.errors,
            status = status.HTTP_400_BAD_REQUEST)


class UserViewset(viewsets.ModelViewSet):
    queryset = User.objects.all()
    # pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    # filterset_fields = ['is_admin']
    serializer_class = UserSerializers
    
    # def get_permissions(self):
    #     if self.action in ['list', 'retrieve']:
    #         return [IsAuthenticated()]  
    #     return []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:       
            serializer.is_valid()
            serializer.save()
        except Exception as e:
            pass 
        return Response(data=serializer.data,
        status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        try:
            instance = self.get_object()
        except ObjectDoesNotExist:
            return Response({'error': 'Object not found'}, status=status.HTTP_404_NOT_FOUND)
        is_verified_raw = request.data.get('is_verified')
        if isinstance(is_verified_raw, str):
            is_verified_in_request = is_verified_raw.lower() in ['true', '1', 'yes']
        elif isinstance(is_verified_raw, bool):
            is_verified_in_request = is_verified_raw
        else:
            is_verified_in_request = False
        should_send_email = (
            'is_verified' in request.data and
            not instance.is_verified and
            is_verified_in_request is True
        )
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if should_send_email:
            to_email = [serializer.instance.email]
            data = {'user': instance, 'instance': instance}
            send_dynamic_email('registration', to_email, data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class UserLogout(generics.GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT,
                        data="User logged out successfully")


class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                data={"OTP sent to your email address."},
                status=status.HTTP_200_OK)
        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)


class OTPVerificationView(APIView):
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        if serializer.is_valid():
            return Response(
                data={"OTP verified successfully."},
                status=status.HTTP_200_OK)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                data={"Password reset successfully."},
                status=status.HTTP_200_OK)
        return Response(
            data=serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def check_refresh_token(request):
    refresh_token = request.data.get('refresh')
    # try:
    payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=['HS256'])
    # except jwt.ExpiredSignatureError:
    #     return JsonResponse({'Token is Expired'})
    # except jwt.InvalidTokenError:
    #     return JsonResponse({'Token is Invalid'})
    # handle invalid token

# check the payload to ensure that the token is valid
    if 'user_id' in payload:
        data ={
            'status':"valid"
        }
        return JsonResponse(
            data,
            status=201,
            headers={'content_type':'application/json'},
            safe=False)
    else:
        data = {
            'status':"invalid"
        }
        return JsonResponse(
            data,
            status=401,
            headers={'content_type':'application/json'},
            safe=False)