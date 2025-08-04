from rest_framework import serializers
from django.utils.encoding import smart_str,force_bytes,DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode,urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from xml.dom import ValidationErr
from django.contrib.auth.hashers import check_password
import random
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework.response import Response
from django.conf import settings
from django.utils import timezone
import string
from datetime import timedelta
from user.email_utils import send_dynamic_email
from .models import User


class UserSerializers(serializers.ModelSerializer):
    class Meta:
        ordering = ['-id']
        model = User
        fields = '__all__'


class UserCreationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(
                            max_length=255,
                            write_only=True)
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        if password != confirm_password:
            raise serializers.ValidationError(
                "password and confirm password didnt matched")
        return attrs
    
    def create(self, validated_data):
        instance = User.objects.create_user(**validated_data)
        to_email = [instance.email]
        otp = generate_otp()
        instance.otp = otp
        instance.otp_created_at = timezone.now()
        instance.save()
        data = {'user': instance, 'instance': instance}
        data['otp'] = instance.otp
        send_dynamic_email('user_verification', to_email, data)
        return instance

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name')
        instance.last_name = validated_data.get('last_name')
        instance.email = validated_data.get('email')
        instance.phone_number = validated_data.get('phone_number')
        instance.save()
        return instance


class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(max_length=250)
    class Meta:
        model = User
        fields =  ['email', 'password']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}
    
    def validate(self, attrs):
        return attrs

    def create(self, validated_data):
        return validated_data


class UserviewSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {'password': {'write_only': True}}
    
    def validate(self, attrs):
        return attrs

    def create(self, validated_data):
        return validated_data


class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(max_length=20)
    password = serializers.CharField(max_length=20)
    confirm_password = serializers.CharField(max_length=20)
    class Meta:
        model = User
        fields = ['password', 'confirm_password', 'old_password']
    def validate(self,attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        user = self.context.get('user')
        if (user.check_password(attrs.get('old_password'))):
            if password == attrs.get('old_password'):
                raise serializers.ValidationError(
                    "Your old password and new password must be different"
                )
            if password != confirm_password:
                raise serializers.ValidationError(
                    "password and confirm password didn't matched"
                    )
            else:
                user.set_password(password)
                user.save()
        else:
            raise serializers.ValidationError(
                "Your old password doesnot matches with the password stored in database"
            )
        return attrs
        

class UserPasswordResetSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=255, style={'input_type':'password'},write_only= True )
    confirm_password = serializers.CharField(max_length=255, style={'input_type':'password'},write_only= True )
    class Meta:
        fields = ['password', 'confirm_password']
        model = User
    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        uid = self.context.get('uid')
        token = self.context.get('token')
        if password != confirm_password:
            raise serializers.ValidationError("password and confirm password didnot matched")
        id = smart_str(urlsafe_base64_decode(uid))
        user = User.objects.get(id=id)
        if not PasswordResetTokenGenerator().check_token(user,token):
            raise ValidationErr('token is not valid or expired')    
        user.set_password(password)
        user.save()
        return attrs

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email.")
        return value

    def create(self, validated_data):
        email = validated_data["email"]
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Email not found.")
        otp = generate_otp()

        user.otp = otp
        user.otp_created_at = timezone.now()
        user.save()
        to_email = [user.email]
        data = {'user': user, 'otp': otp}
        send_dynamic_email('forgot_password', to_email, data)
        return validated_data

    
class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()
    new_password = serializers.CharField()

    def validate_otp(self, value):
        email = self.initial_data.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP or email.")

        if user.otp != value:
            raise serializers.ValidationError("Invalid OTP.")

        expiration_time = user.otp_created_at + timedelta(minutes=3)
        if timezone.now() > expiration_time:
            raise serializers.ValidationError("OTP has expired.")

        user.otp = None
        user.otp_created_at = None
        user.save()
        return value

    def create(self, validated_data):
        email = validated_data['email']
        new_password = validated_data['new_password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")

        user.set_password(new_password)
        user.save()

        return validated_data

class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()

    def validate(self, data):
        email = data.get('email')
        otp = data.get('otp')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP or email.")

        if user.otp != otp:
            raise serializers.ValidationError("Invalid OTP.")

        expiration_time = user.otp_created_at + timedelta(minutes=5)
        if timezone.now() > expiration_time:
            raise serializers.ValidationError("OTP has expired.")
        return data


class ResetPasswordOtp(serializers.Serializer):
    pass

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    default_error_message = {
        'bad_token': ('Token is expired or invalid')
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self, **kwargs):
        try:
            RefreshToken(self.token).blacklist()
        except TokenError:
            self.fail('bad_token')
