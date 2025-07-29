# authentication/serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True, min_length=3,
                                     max_length=150)
    email = serializers.EmailField(required=True, max_length=320)
    password = serializers.CharField(write_only=True, required=True,
                                     style={'input_type': 'password'}, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True,
                                      style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']

    def validate(self, attrs):
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError(
                {"username": "A user with that username already exists."})

        if User.objects.filter(email__iexact=attrs['email']).exists():
            raise serializers.ValidationError(
                {"email": "A user with that email already exists."})

        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user
