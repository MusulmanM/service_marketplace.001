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
    # Frontend-friendly aliases
    phone = serializers.CharField(source="phone_number", read_only=True)
    role = serializers.CharField(source="user_type", read_only=True)
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "phone_number",
            "phone",
            "email",
            "user_type",
            "role",
            "first_name",
            "last_name",
            "avatar",
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

    def get_first_name(self, obj):
        profile = getattr(obj, "profile", None)
        return profile.first_name if profile else ""

    def get_last_name(self, obj):
        profile = getattr(obj, "profile", None)
        return profile.last_name if profile else ""

    def get_avatar(self, obj):
        profile = getattr(obj, "profile", None)
        if profile and profile.avatar:
            request = self.context.get("request")
            url = profile.avatar.url
            return request.build_absolute_uri(url) if request else url
        return None


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
    """Accepts phone/phone_number, role/user_type, first_name, last_name, password (+ confirm)."""

    password = serializers.CharField(write_only=True, min_length=8, style={"input_type": "password"})
    password_confirm = serializers.CharField(write_only=True, style={"input_type": "password"})
    phone = serializers.CharField(write_only=True, required=False)
    role = serializers.ChoiceField(
        choices=((UserType.CLIENT, "Client"), (UserType.MASTER, "Master")),
        required=False,
        write_only=True,
    )
    user_type = serializers.ChoiceField(
        choices=((UserType.CLIENT, "Client"), (UserType.MASTER, "Master")),
        default=UserType.CLIENT,
        required=False,
    )
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=100, write_only=True)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=100, write_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "phone_number",
            "phone",
            "email",
            "user_type",
            "role",
            "first_name",
            "last_name",
            "password",
            "password_confirm",
        )
        read_only_fields = ("id",)
        extra_kwargs = {"phone_number": {"required": False}}

    def validate(self, attrs):
        phone = attrs.get("phone_number") or attrs.get("phone") or self.initial_data.get("phone")
        if not phone:
            raise serializers.ValidationError({"phone_number": "Phone number is required."})
        phone = str(phone).strip().replace(" ", "")
        if User.objects.filter(phone_number=phone).exists():
            raise serializers.ValidationError({"phone_number": "User with this phone number already exists."})
        attrs["phone_number"] = phone
        attrs.pop("phone", None)

        role = attrs.pop("role", None) or attrs.get("user_type") or self.initial_data.get("role")
        if role:
            role = str(role).lower().strip()
            if role not in (UserType.CLIENT, UserType.MASTER):
                raise serializers.ValidationError({"role": "Role must be client or master."})
            attrs["user_type"] = role
        else:
            attrs.setdefault("user_type", UserType.CLIENT)

        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        first_name = (validated_data.pop("first_name", "") or "").strip()
        last_name = (validated_data.pop("last_name", "") or "").strip()
        password = validated_data.pop("password")
        validated_data.pop("phone", None)
        validated_data.pop("role", None)

        user = User.objects.create_user(password=password, **validated_data)
        profile, _ = UserProfile.objects.get_or_create(user=user)
        if first_name or last_name:
            profile.first_name = first_name
            profile.last_name = last_name
            profile.save(update_fields=["first_name", "last_name", "updated_at"])

        if user.user_type == UserType.MASTER:
            from masters.models import MasterProfile

            full = f"{first_name} {last_name}".strip()
            MasterProfile.objects.get_or_create(
                user=user,
                defaults={
                    "name": full or user.phone_number,
                    "is_available": True,
                },
            )

        return user

    def to_representation(self, instance):
        return UserSerializer(instance, context=self.context).data


class PhoneTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Accepts phone_number (USERNAME_FIELD) or legacy `phone` in the request body."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field].required = False
        self.fields["phone"] = serializers.CharField(required=False, write_only=True)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["phone_number"] = user.phone_number
        token["user_type"] = user.user_type
        return token

    def validate(self, attrs):
        phone = attrs.get("phone") or self.initial_data.get("phone")
        if not attrs.get(self.username_field) and phone:
            attrs[self.username_field] = str(phone).strip().replace(" ", "")
        if not attrs.get(self.username_field):
            raise serializers.ValidationError(
                {self.username_field: "Phone number is required."}
            )
        attrs.pop("phone", None)
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user, context=self.context).data
        return data
