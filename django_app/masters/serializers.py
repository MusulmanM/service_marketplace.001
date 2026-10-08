from rest_framework import serializers

from users.models import UserType
from users.serializers import UserBriefSerializer

from .models import MasterProfile, MasterService, ServiceCategory, ServiceCity


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ("id", "name", "slug", "description", "is_active", "created_at")
        read_only_fields = ("id", "created_at")


class ServiceCitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCity
        fields = ("id", "name", "slug", "is_active", "created_at")
        read_only_fields = ("id", "created_at")


class MasterProfileSerializer(serializers.ModelSerializer):
    user = UserBriefSerializer(read_only=True)
    categories = ServiceCategorySerializer(many=True, read_only=True)
    cities = ServiceCitySerializer(many=True, read_only=True)
    category_ids = serializers.PrimaryKeyRelatedField(
        queryset=ServiceCategory.objects.filter(is_active=True),
        many=True,
        write_only=True,
        required=False,
        source="categories",
    )
    city_ids = serializers.PrimaryKeyRelatedField(
        queryset=ServiceCity.objects.filter(is_active=True),
        many=True,
        write_only=True,
        required=False,
        source="cities",
    )

    class Meta:
        model = MasterProfile
        fields = (
            "id",
            "user",
            "name",
            "avatar",
            "title",
            "description",
            "experience_years",
            "rating",
            "reviews_count",
            "categories",
            "category_ids",
            "cities",
            "city_ids",
            "city",
            "is_available",
            "is_verified",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "user",
            "rating",
            "reviews_count",
            "is_verified",
            "created_at",
            "updated_at",
        )

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Master name is required.")
        return value.strip()

    def validate(self, attrs):
        request = self.context.get("request")
        if request and request.user.is_authenticated and request.user.user_type != UserType.MASTER:
            raise serializers.ValidationError("Only users with master role can manage master profiles.")
        return attrs

    def create(self, validated_data):
        categories = validated_data.pop("categories", [])
        cities = validated_data.pop("cities", [])
        request = self.context["request"]

        if MasterProfile.objects.filter(user=request.user).exists():
            raise serializers.ValidationError("Master profile already exists.")

        profile = MasterProfile.objects.create(user=request.user, **validated_data)
        profile.categories.set(categories)
        profile.cities.set(cities)
        return profile

    def update(self, instance, validated_data):
        categories = validated_data.pop("categories", None)
        cities = validated_data.pop("cities", None)
        instance = super().update(instance, validated_data)
        if categories is not None:
            instance.categories.set(categories)
        if cities is not None:
            instance.cities.set(cities)
        return instance


class MasterServiceSerializer(serializers.ModelSerializer):
    master = MasterProfileSerializer(read_only=True)
    category = ServiceCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=ServiceCategory.objects.filter(is_active=True),
        source="category",
        write_only=True,
    )

    class Meta:
        model = MasterService
        fields = (
            "id",
            "master",
            "category",
            "category_id",
            "title",
            "description",
            "price",
            "duration_minutes",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "master", "created_at", "updated_at")

    def validate(self, attrs):
        request = self.context.get("request")
        if request and request.user.is_authenticated and request.user.user_type != UserType.MASTER:
            raise serializers.ValidationError("Only masters can manage services.")
        if request and request.user.is_authenticated and not hasattr(request.user, "master_profile"):
            raise serializers.ValidationError("Create a master profile before adding services.")
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        return MasterService.objects.create(master=request.user.master_profile, **validated_data)
