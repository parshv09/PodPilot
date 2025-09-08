from rest_framework import serializers
# from django.contrib.auth import authenticate
from .models import User
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from .models import EmailOTP
import random
from django.core.mail import send_mail
from datetime import timedelta

class UserSerializer(serializers.ModelSerializer):
    """Serializer for returning user details."""
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'profile_image']

    def get_profile_image(self, obj):
        # If user uploaded their own image
        if obj.profile_image:
            request = self.context.get("request")
            if request is not None:
                return request.build_absolute_uri(obj.profile_image.url)
            return obj.profile_image.url

        # Else, return Google image URL
        if obj.profile_image_url:
            return obj.profile_image_url

        return None


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration with strong password validation."""
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'profile_image', 'password']

    def validate_password(self, value):
        # Use Django's built-in validators
        validate_password(value)
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

from django.contrib.auth import get_user_model

User = get_user_model()

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data['email']
        password = data['password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password")

        if not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled")

        data['user'] = user
        return data


class RequestOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value

    def create(self, validated_data):
        email = validated_data['email']
        otp = str(random.randint(100000, 999999))
        expires_at = timezone.now() + timedelta(minutes=10)

        # Remove any previous OTPs for the email
        EmailOTP.objects.filter(email=email).delete()

        # Create new OTP entry
        email_otp = EmailOTP.objects.create(email=email, otp=otp, expires_at=expires_at)

        # Send OTP email
        send_mail(
            subject="Your OTP for Registration",
            message=f"Your OTP is {otp}. It will expire in 10 minutes.",
            from_email="no-reply@example.com",
            recipient_list=[email],
            fail_silently=False
        )

        return email_otp


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        otp = attrs.get('otp')

        try:
            email_otp = EmailOTP.objects.get(email=email, otp=otp)
        except EmailOTP.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP.")

        if email_otp.is_expired():
            raise serializers.ValidationError("OTP has expired.")

        attrs['email_otp'] = email_otp
        return attrs

    def create(self, validated_data):
        email_otp = validated_data.pop('email_otp')
        email_otp.is_verified = True
        email_otp.save()

        user = User.objects.create_user(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            password=validated_data['password']
        )

        # After creation, remove the OTP entry
        email_otp.delete()
        return user
