from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from users.models import UserType
from users.permissions import IsClientRole

from .models import Order, OrderReview, OrderStatus
from .serializers import (
    OrderCreateSerializer,
    OrderPhotoSerializer,
    OrderReportSerializer,
    OrderReviewSerializer,
    OrderSerializer,
    OrderStatusUpdateSerializer,
)


def get_master_profile(user):
    return getattr(user, "master_profile", None)


def is_admin_user(user):
    return bool(user and user.is_authenticated and (user.is_staff or user.user_type == UserType.ADMIN))


class OrderViewSet(viewsets.ModelViewSet):
    parser_classes = (JSONParser, MultiPartParser, FormParser)

    def get_queryset(self):
        queryset = (
            Order.objects.select_related(
                "client",
                "master",
                "master__user",
                "service",
                "service__category",
            )
            .prefetch_related(
                "master__categories",
                "master__cities",
                "photos",
                "status_history",
            )
            .all()
        )

        user = self.request.user
        if not user.is_authenticated:
            return queryset.none()

        if is_admin_user(user):
            pass
        elif user.user_type == UserType.CLIENT:
            queryset = queryset.filter(client=user)
        elif user.user_type == UserType.MASTER:
            master_profile = get_master_profile(user)
            queryset = queryset.filter(master=master_profile) if master_profile else queryset.none()
        else:
            return queryset.none()

        status_filter = self.request.query_params.get("status")
        if status_filter:
            status_filter = status_filter.lower()
            allowed_values = {choice.value for choice in OrderStatus}
            queryset = queryset.filter(status=status_filter) if status_filter in allowed_values else queryset.none()

        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return OrderCreateSerializer
        if self.action == "change_status":
            return OrderStatusUpdateSerializer
        return OrderSerializer

    def get_permissions(self):
        if self.action == "create":
            return [permissions.IsAuthenticated(), IsClientRole()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save()

    def ensure_participant_or_admin(self, order):
        user = self.request.user
        if is_admin_user(user) or order.client_id == user.id:
            return
        master_profile = get_master_profile(user)
        if master_profile and order.master_id == master_profile.id:
            return
        raise PermissionDenied("You must be a participant of this order.")

    def ensure_assigned_master_or_admin(self, order):
        user = self.request.user
        if is_admin_user(user):
            return
        master_profile = get_master_profile(user)
        if master_profile and order.master_id == master_profile.id:
            return
        raise PermissionDenied("Only the assigned master can perform this action.")

    def ensure_order_client(self, order):
        if order.client_id != self.request.user.id:
            raise PermissionDenied("Only the order client can perform this action.")

    @action(detail=True, methods=["patch"], url_path="status")
    def change_status(self, request, pk=None):
        order = self.get_object()
        self.ensure_assigned_master_or_admin(order)

        serializer = OrderStatusUpdateSerializer(data=request.data, context={"order": order})
        serializer.is_valid(raise_exception=True)

        order.set_status(
            serializer.validated_data["status"],
            changed_by=request.user,
            comment=serializer.validated_data.get("comment", ""),
        )
        return Response(OrderSerializer(order, context=self.get_serializer_context()).data)

    @action(detail=True, methods=["get", "post"], url_path="photos")
    def photos(self, request, pk=None):
        order = self.get_object()
        self.ensure_participant_or_admin(order)

        if request.method == "GET":
            serializer = OrderPhotoSerializer(
                order.photos.all(),
                many=True,
                context=self.get_serializer_context(),
            )
            return Response(serializer.data)

        serializer = OrderPhotoSerializer(
            data=request.data,
            context={**self.get_serializer_context(), "order": order},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get", "post", "put", "patch"], url_path="report")
    def report(self, request, pk=None):
        order = self.get_object()
        self.ensure_participant_or_admin(order)
        report = getattr(order, "report", None)

        if request.method == "GET":
            if report is None:
                raise NotFound("Report was not created yet.")
            serializer = OrderReportSerializer(report, context=self.get_serializer_context())
            return Response(serializer.data)

        self.ensure_assigned_master_or_admin(order)

        if request.method == "POST":
            if report is not None:
                raise ValidationError("Report already exists. Use PUT or PATCH to update it.")
            serializer = OrderReportSerializer(
                data=request.data,
                context={**self.get_serializer_context(), "order": order},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(order=order, master=order.master)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if report is None:
            raise NotFound("Report was not created yet.")

        serializer = OrderReportSerializer(
            report,
            data=request.data,
            partial=request.method == "PATCH",
            context={**self.get_serializer_context(), "order": order},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=["get", "post", "put", "patch"], url_path="review")
    def review(self, request, pk=None):
        order = self.get_object()
        self.ensure_participant_or_admin(order)
        review = getattr(order, "review", None)

        if request.method == "GET":
            if review is None:
                raise NotFound("Review was not created yet.")
            serializer = OrderReviewSerializer(review, context=self.get_serializer_context())
            return Response(serializer.data)

        self.ensure_order_client(order)

        if request.method == "POST":
            if OrderReview.objects.filter(order=order).exists():
                raise ValidationError("Review already exists. Use PUT or PATCH to update it.")
            serializer = OrderReviewSerializer(
                data=request.data,
                context={**self.get_serializer_context(), "order": order},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(order=order, client=request.user, master=order.master)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if review is None:
            raise NotFound("Review was not created yet.")

        serializer = OrderReviewSerializer(
            review,
            data=request.data,
            partial=request.method == "PATCH",
            context={**self.get_serializer_context(), "order": order},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
