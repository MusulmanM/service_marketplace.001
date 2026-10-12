from rest_framework import serializers

from masters.models import MasterProfile, MasterService
from masters.serializers import MasterProfileSerializer, MasterServiceSerializer
from users.models import UserType
from users.serializers import UserBriefSerializer

from .models import (
    Order,
    OrderPhoto,
    OrderPhotoKind,
    OrderReport,
    OrderReview,
    OrderStatus,
    OrderStatusHistory,
)


def is_admin_user(user):
    return bool(user and user.is_authenticated and (user.is_staff or user.user_type == UserType.ADMIN))


def get_master_profile(user):
    return getattr(user, "master_profile", None)


def client_display_name(user):
    profile = getattr(user, "profile", None)
    if profile:
        full = f"{profile.first_name or ''} {profile.last_name or ''}".strip()
        if full:
            return full
    return user.phone_number


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    changed_by = UserBriefSerializer(read_only=True)

    class Meta:
        model = OrderStatusHistory
        fields = ("id", "old_status", "new_status", "changed_by", "comment", "created_at")
        read_only_fields = fields


class OrderPhotoSerializer(serializers.ModelSerializer):
    uploaded_by = UserBriefSerializer(read_only=True)
    # Accept legacy "photo_type" from older clients
    photo_type = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = OrderPhoto
        fields = (
            "id",
            "order",
            "uploaded_by",
            "kind",
            "photo_type",
            "image",
            "caption",
            "created_at",
        )
        read_only_fields = ("id", "order", "uploaded_by", "created_at")
        extra_kwargs = {"kind": {"required": False}}

    def validate(self, attrs):
        if not attrs.get("kind") and attrs.get("photo_type"):
            attrs["kind"] = attrs.pop("photo_type")
        elif "photo_type" in attrs:
            attrs.pop("photo_type")

        if not attrs.get("kind"):
            raise serializers.ValidationError({"kind": "This field is required."})

        order = self.context.get("order")
        request = self.context.get("request")
        if not order or not request:
            return attrs

        user = request.user
        master_profile = get_master_profile(user)
        is_client = order.client_id == user.id
        is_master = bool(master_profile and order.master_id == master_profile.id)

        if not (is_client or is_master or is_admin_user(user)):
            raise serializers.ValidationError("Only order participants can upload photos.")

        if attrs.get("kind") == OrderPhotoKind.AFTER and not (is_master or is_admin_user(user)):
            raise serializers.ValidationError("Only the assigned master can upload after photos.")

        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        order = self.context["order"]
        validated_data.pop("photo_type", None)
        return OrderPhoto.objects.create(order=order, uploaded_by=request.user, **validated_data)


class OrderReportSerializer(serializers.ModelSerializer):
    master = MasterProfileSerializer(read_only=True)
    # Accept legacy "text" field as summary
    text = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = OrderReport
        fields = (
            "id",
            "order",
            "master",
            "summary",
            "text",
            "labor_cost",
            "parts_cost",
            "total",
            "warranty_days",
            "checklist",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "order", "master", "created_at", "updated_at")
        extra_kwargs = {"summary": {"required": False}}

    def validate(self, attrs):
        if not attrs.get("summary") and attrs.get("text"):
            attrs["summary"] = attrs.pop("text")
        elif "text" in attrs:
            attrs.pop("text")

        if self.instance is None and not attrs.get("summary"):
            raise serializers.ValidationError({"summary": "This field is required."})

        order = self.context.get("order")
        request = self.context.get("request")
        if not order or not request:
            return attrs

        user = request.user
        master_profile = get_master_profile(user)
        is_master = bool(master_profile and order.master_id == master_profile.id)
        if not (is_master or is_admin_user(user)):
            raise serializers.ValidationError("Only the assigned master can create a report.")

        if order.status not in (OrderStatus.IN_PROGRESS, OrderStatus.COMPLETED, OrderStatus.ON_SITE):
            raise serializers.ValidationError(
                "Report can be created only for on-site, in-progress, or completed orders."
            )

        checklist = attrs.get("checklist")
        if checklist is not None and not isinstance(checklist, (list, dict)):
            raise serializers.ValidationError({"checklist": "Checklist must be a list or an object."})

        labor = attrs.get("labor_cost")
        parts = attrs.get("parts_cost")
        if attrs.get("total") is None and (labor is not None or parts is not None):
            from decimal import Decimal

            attrs["total"] = (labor or Decimal("0")) + (parts or Decimal("0"))

        return attrs


class OrderReviewSerializer(serializers.ModelSerializer):
    client = UserBriefSerializer(read_only=True)
    master = MasterProfileSerializer(read_only=True)

    class Meta:
        model = OrderReview
        fields = ("id", "order", "client", "master", "rating", "comment", "created_at", "updated_at")
        read_only_fields = ("id", "order", "client", "master", "created_at", "updated_at")

    def validate(self, attrs):
        order = self.context.get("order") or getattr(self.instance, "order", None)
        request = self.context.get("request")
        if not order or not request:
            return attrs

        if request.user.user_type != UserType.CLIENT or order.client_id != request.user.id:
            raise serializers.ValidationError("Only the order client can leave a review.")

        if order.status != OrderStatus.COMPLETED:
            raise serializers.ValidationError("Review can be created only for completed orders.")

        exists = OrderReview.objects.filter(order=order)
        if self.instance:
            exists = exists.exclude(pk=self.instance.pk)
        if exists.exists():
            raise serializers.ValidationError("Review for this order already exists.")

        return attrs


class OrderSerializer(serializers.ModelSerializer):
    client = UserBriefSerializer(read_only=True)
    master = MasterProfileSerializer(read_only=True)
    service = MasterServiceSerializer(read_only=True)
    photos = OrderPhotoSerializer(many=True, read_only=True)
    report = OrderReportSerializer(read_only=True)
    review = OrderReviewSerializer(read_only=True)
    status_history = OrderStatusHistorySerializer(many=True, read_only=True)
    number = serializers.CharField(read_only=True)
    client_name = serializers.SerializerMethodField()
    client_phone = serializers.CharField(source="client.phone_number", read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "number",
            "client",
            "client_name",
            "client_phone",
            "master",
            "service",
            "title",
            "description",
            "address",
            "price",
            "status",
            "scheduled_at",
            "completed_at",
            "created_at",
            "updated_at",
            "photos",
            "report",
            "review",
            "status_history",
        )
        read_only_fields = fields

    def get_client_name(self, obj):
        return client_display_name(obj.client)


class OrderCreateSerializer(serializers.ModelSerializer):
    master = serializers.PrimaryKeyRelatedField(queryset=MasterProfile.objects.filter(is_available=True))
    service = serializers.PrimaryKeyRelatedField(
        queryset=MasterService.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    title = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Order
        fields = ("id", "master", "service", "title", "description", "address", "price", "scheduled_at")
        read_only_fields = ("id",)

    def validate(self, attrs):
        request = self.context["request"]
        if request.user.user_type != UserType.CLIENT:
            raise serializers.ValidationError("Only clients can create orders.")

        service = attrs.get("service")
        master = attrs["master"]
        if service and service.master_id != master.id:
            raise serializers.ValidationError({"service": "Selected service does not belong to this master."})

        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        service = validated_data.get("service")
        description = validated_data.get("description", "")

        if service and not validated_data.get("price"):
            validated_data["price"] = service.price
        if not validated_data.get("title"):
            validated_data["title"] = service.title if service else description[:120]

        return Order.objects.create(client=request.user, **validated_data)

    def to_representation(self, instance):
        return OrderSerializer(instance, context=self.context).data


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.CharField()
    comment = serializers.CharField(required=False, allow_blank=True)

    def validate_status(self, value):
        value = value.lower()
        # Map legacy "pending" to "new"
        if value == "pending":
            value = OrderStatus.NEW
        allowed_values = {choice.value for choice in OrderStatus}
        if value not in allowed_values:
            raise serializers.ValidationError(f"Status must be one of: {', '.join(sorted(allowed_values))}.")
        return value

    def validate(self, attrs):
        order = self.context["order"]
        new_status = attrs["status"]

        if order.status == new_status:
            raise serializers.ValidationError({"status": "Order already has this status."})
        if not order.can_transition_to(new_status):
            raise serializers.ValidationError(
                {"status": f"Cannot change status from {order.status} to {new_status}."}
            )
        return attrs
