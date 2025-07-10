from rest_framework import serializers
from django.contrib import auth
from rest_framework.exceptions import AuthenticationFailed
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255)
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=['admin', 'user'])
    username = serializers.CharField(read_only=True)
    id = serializers.IntegerField(read_only=True)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        role = attrs.get('role')

        user = auth.authenticate(email=email, password=password)

        if not user:
            raise AuthenticationFailed("Invalid credentials")

        if not user.is_active:
            raise AuthenticationFailed("Account is disabled")

        # Role-based check
        if role == "admin" and not user.is_staff:
            raise AuthenticationFailed("User is not an admin")
        elif role == "user" and user.is_staff:
            raise AuthenticationFailed("Admins cannot log in as user")

        refresh = RefreshToken.for_user(user)

        return {
            'email': user.email,
            'username': user.username,
            'id': user.id,
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }



class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modules
        fields = ['id', 'module_name']