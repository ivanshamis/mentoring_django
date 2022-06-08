from django.contrib.auth import authenticate
from rest_framework import serializers

from user.backends import validate_token
from user.constants import ErrorMessages, MIN_PASSWORD_LENGTH
from user.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128, min_length=MIN_PASSWORD_LENGTH, write_only=True
    )

    class Meta:
        model = User
        fields = ["email", "username", "password"]

    def create(self, validated_data):
        return self.Meta.model.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255, write_only=True)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def create(self, validated_data):
        user = authenticate(
            username=validated_data["username"], password=validated_data["password"]
        )
        if not user:
            raise serializers.ValidationError(ErrorMessages.USER_WRONG_CREDENTIALS)
        if not user.is_active:
            raise serializers.ValidationError(ErrorMessages.USER_IS_DEACTIVATED)

        return user

    def update(self, instance, validated_data):
        pass


class ActivationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=255, read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    def validate(self, data):
        user = validate_token(
            token=self.context["request"].query_params.get("token"), action="activate"
        )
        if not user:
            raise serializers.ValidationError(ErrorMessages.INVALID_TOKEN)
        data["user"] = user
        return data

    def create(self, validated_data):
        user = validated_data["user"]
        user.is_active = True
        user.save()
        return user

    def update(self, instance, validated_data):
        pass


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
        )
        read_only_fields_for_all = ("id", "email")
        read_only_fields = read_only_fields_for_all + ("is_active", "is_staff")

    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            if key == "password":
                instance.set_password(value)
            else:
                setattr(instance, key, value)

        instance.save()

        return instance


class AdminSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        read_only_fields = UserSerializer.Meta.read_only_fields_for_all + ("password",)


class AdminCreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "username", "is_staff"]

    def create(self, validated_data):
        return self.Meta.model.objects.create_user(**validated_data)
