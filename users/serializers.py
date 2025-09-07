from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User
from django.contrib.auth.password_validation import validate_password


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


