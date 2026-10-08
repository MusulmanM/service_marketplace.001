import uuid
from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg, Count


class ServiceCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Service categories"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.name


class ServiceCity(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Service cities"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return self.name


def master_avatar_upload_path(instance, filename):
    return f"masters/{instance.user_id}/avatar/{filename}"


class MasterProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="master_profile",
        limit_choices_to={"user_type": "master"},
    )
    name = models.CharField(max_length=150, blank=True, default="")
    avatar = models.ImageField(upload_to=master_avatar_upload_path, blank=True, null=True)
    title = models.CharField(max_length=150, blank=True, default="")
    description = models.TextField(blank=True, default="")
    experience_years = models.PositiveSmallIntegerField(
        default=0,
        validators=[MaxValueValidator(80)],
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )
    reviews_count = models.PositiveIntegerField(default=0, editable=False)
    categories = models.ManyToManyField(
        ServiceCategory,
        related_name="masters",
        blank=True,
    )
    cities = models.ManyToManyField(
        ServiceCity,
        related_name="masters",
        blank=True,
    )
    is_available = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    city = models.CharField(max_length=100, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-rating", "-created_at"]
        indexes = [
            models.Index(fields=["is_available"]),
            models.Index(fields=["is_verified"]),
            models.Index(fields=["city"]),
            models.Index(fields=["rating"]),
            models.Index(fields=["created_at"]),
        ]

    def recalculate_rating(self):
        summary = self.reviews.aggregate(avg=Avg("rating"), count=Count("id"))
        average = summary["avg"] or Decimal("0")
        if not isinstance(average, Decimal):
            average = Decimal(str(average))
        self.rating = average.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        self.reviews_count = summary["count"] or 0
        self.save(update_fields=["rating", "reviews_count", "updated_at"])

    def __str__(self):
        return self.name or f"Master: {self.user.phone_number}"


class MasterService(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    master = models.ForeignKey(
        MasterProfile,
        on_delete=models.CASCADE,
        related_name="services",
    )
    category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.PROTECT,
        related_name="master_services",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.PositiveIntegerField(default=60)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["price"]
        indexes = [
            models.Index(fields=["is_active"]),
            models.Index(fields=["price"]),
        ]

    def __str__(self):
        return f"{self.title} - {self.master}"
