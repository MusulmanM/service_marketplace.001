import uuid
from decimal import Decimal

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Max
from django.utils import timezone


class OrderStatus(models.TextChoices):
    NEW = "new", "New"
    ACCEPTED = "accepted", "Accepted"
    EN_ROUTE = "en_route", "En route"
    ON_SITE = "on_site", "On site"
    IN_PROGRESS = "in_progress", "In progress"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"
    REJECTED = "rejected", "Rejected"


class OrderPhotoKind(models.TextChoices):
    BEFORE = "before", "Before"
    AFTER = "after", "After"


# Backward-compatible alias
OrderPhotoType = OrderPhotoKind


ORDER_STATUS_TRANSITIONS = {
    OrderStatus.NEW: {OrderStatus.ACCEPTED, OrderStatus.REJECTED, OrderStatus.CANCELLED},
    OrderStatus.ACCEPTED: {OrderStatus.EN_ROUTE, OrderStatus.CANCELLED},
    OrderStatus.EN_ROUTE: {OrderStatus.ON_SITE, OrderStatus.CANCELLED},
    OrderStatus.ON_SITE: {OrderStatus.IN_PROGRESS, OrderStatus.CANCELLED},
    OrderStatus.IN_PROGRESS: {OrderStatus.COMPLETED, OrderStatus.CANCELLED},
    OrderStatus.COMPLETED: set(),
    OrderStatus.CANCELLED: set(),
    OrderStatus.REJECTED: set(),
}


def next_order_number():
    latest = Order.objects.aggregate(m=Max("number_seq")).get("m") or 0
    return latest + 1


class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    number_seq = models.PositiveIntegerField(unique=True, null=True, blank=True, editable=False)
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client_orders",
        limit_choices_to={"user_type": "client"},
    )
    master = models.ForeignKey(
        "masters.MasterProfile",
        on_delete=models.CASCADE,
        related_name="orders",
    )
    service = models.ForeignKey(
        "masters.MasterService",
        on_delete=models.PROTECT,
        related_name="orders",
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=200, blank=True, default="")
    description = models.TextField(blank=True, default="")
    address = models.CharField(max_length=255, blank=True, default="")
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.NEW,
    )
    scheduled_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["client"]),
            models.Index(fields=["master"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["scheduled_at"]),
            models.Index(fields=["number_seq"]),
        ]

    @property
    def number(self):
        if self.number_seq:
            return f"SM-{self.number_seq:05d}"
        return f"SM-{str(self.id)[:8].upper()}"

    def __str__(self):
        return f"Order {self.number} [{self.status}]"

    def save(self, *args, **kwargs):
        if self.number_seq is None:
            self.number_seq = next_order_number()
        super().save(*args, **kwargs)

    def can_transition_to(self, new_status):
        return new_status in ORDER_STATUS_TRANSITIONS.get(self.status, set())

    def set_status(self, new_status, changed_by=None, comment=""):
        old_status = self.status
        if old_status == new_status:
            return self

        self.status = new_status
        update_fields = ["status", "updated_at"]
        if new_status == OrderStatus.COMPLETED:
            self.completed_at = timezone.now()
            update_fields.append("completed_at")
        elif old_status == OrderStatus.COMPLETED:
            self.completed_at = None
            update_fields.append("completed_at")

        self.save(update_fields=update_fields)
        OrderStatusHistory.objects.create(
            order=self,
            old_status=old_status,
            new_status=new_status,
            changed_by=changed_by,
            comment=comment,
        )
        return self


class OrderStatusHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="status_history",
    )
    old_status = models.CharField(max_length=20, blank=True, default="")
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    comment = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Order status histories"

    def __str__(self):
        return f"{self.order_id}: {self.old_status} -> {self.new_status}"


def order_photo_upload_path(instance, filename):
    return f"orders/{instance.order_id}/{instance.kind}/{filename}"


class OrderPhoto(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="photos",
    )
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="order_photos",
    )
    kind = models.CharField(
        max_length=10,
        choices=OrderPhotoKind.choices,
    )
    image = models.ImageField(upload_to=order_photo_upload_path)
    caption = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["order", "kind"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.order_id}: {self.kind}"


class OrderReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="report",
    )
    master = models.ForeignKey(
        "masters.MasterProfile",
        on_delete=models.CASCADE,
        related_name="reports",
    )
    summary = models.TextField()
    labor_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    parts_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0"))
    warranty_days = models.PositiveIntegerField(default=30)
    checklist = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if self.total in (None, Decimal("0")) and (self.labor_cost or self.parts_cost):
            self.total = (self.labor_cost or Decimal("0")) + (self.parts_cost or Decimal("0"))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Report for order {self.order_id}"


class OrderReview(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="review",
    )
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="order_reviews",
        limit_choices_to={"user_type": "client"},
    )
    master = models.ForeignKey(
        "masters.MasterProfile",
        on_delete=models.CASCADE,
        related_name="reviews",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["master", "rating"]),
            models.Index(fields=["client"]),
            models.Index(fields=["created_at"]),
        ]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.master.recalculate_rating()

    def delete(self, *args, **kwargs):
        master = self.master
        result = super().delete(*args, **kwargs)
        master.recalculate_rating()
        return result

    def __str__(self):
        return f"{self.master_id}: {self.rating}"
