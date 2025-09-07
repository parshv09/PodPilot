from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer
from rest_framework import status
from django.conf import settings
from django.contrib.auth import get_user_model
from google.oauth2 import id_token 
from google.auth.transport import requests 
from rest_framework.views import APIView



class RegisterView(generics.CreateAPIView):
    """Handles user registration."""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class LoginView(generics.GenericAPIView):
    """Handles user login and returns JWT tokens."""
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        })

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklist the token
            return Response({"detail": "Logout successful"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)





User = get_user_model()

class GoogleLoginView(APIView):
    def post(self, request):
        token = request.data.get("id_token")

        try:
            # Verify token using Google
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), settings.GOOGLE_CLIENT_ID)

            email = idinfo.get("email")
            name = idinfo.get("name")  # Full name from Google
            picture = idinfo.get("picture")

            if not email:
                return Response({"error": "Email not available from Google"}, status=status.HTTP_400_BAD_REQUEST)

            # Split name into first and last (if possible)
            first_name, last_name = "", ""
            if name:
                parts = name.split(" ", 1)
                first_name = parts[0]
                if len(parts) > 1:
                    last_name = parts[1]

            # Get or create user
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "profile_image_url": picture
                }
            )

             # If user already existed, update profile image if needed
            if not created and picture and user.profile_image_url != picture:
                user.profile_image_url = picture
                user.save()


            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "profile_image": user.profile_image.url if user.profile_image else user.profile_image_url,
                }
            })

        except ValueError:
            return Response({"error": "Invalid Google token"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Server error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
