from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import UserProfile, UserType

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            "id",
            "first_name",
            "last_name",
            "full_name",
            "avatar",
            "gender",
            "bio",
            "birth_date",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "full_name", "created_at", "updated_at")


class UserBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "phone_number", "user_type", "is_verified")
        read_only_fields = fields


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "phone_number",
            "email",
            "user_type",
            "is_verified",
            "created_at",
            "updated_at",
            "profile",
        )
        read_only_fields = (
            "id",
            "user_type",
            "is_verified",
            "created_at",
            "updated_at",
        )


class UserUpdateSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ("phone_number", "email", "profile")

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        update_fields = [*validated_data.keys(), "updated_at"]
        instance.save(update_fields=update_fields)

        if profile_data is not None:
            profile, _ = UserProfile.objects.get_or_create(user=instance)
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance

    def to_representation(self, instance):
        return UserSerializer(instance, context=self.context).data


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, style={"input_type": "password"})
    password_confirm = serializers.CharField(write_only=True, style={"input_type": "password"})
    user_type = serializers.ChoiceField(
        choices=((UserType.CLIENT, "Client"), (UserType.MASTER, "Master")),
        default=UserType.CLIENT,
    )

    class Meta:
        model = User
        fields = ("id", "phone_number", "email", "user_type", "password", "password_confirm")
        read_only_fields = ("id",)

    def validate_phone_number(self, value):
        value = value.strip().replace(" ", "")
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("User with this phone number already exists.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        UserProfile.objects.get_or_create(user=user)
        return user

    def to_representation(self, instance):
        return UserSerializer(instance, context=self.context).data


class PhoneTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["phone_number"] = user.phone_number
        token["user_type"] = user.user_type
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user, context=self.context).data
        return data
