from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import (
    validate_password,
)  # djagno 기본 패스워드 검증 도구

from rest_framework import serializers
from rest_framework.authtoken.models import Token  # 토큰 모델
from rest_framework.validators import UniqueValidator  # 이메일 중복 검사

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("nickname", "position", "subjects", "image")


class ResisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("username", "password", "password2", "email")

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
        )
        user.set_password(validated_data["password"])
        user.save()
        token = Token.objects.create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user:
            token = Token.objects.get(user=user)
            return token
        raise serializers.ValidationError(
            {"error": "Unable to log in with provided credentials."}
        )
