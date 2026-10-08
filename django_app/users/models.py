import random
import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone


class UserType(models.TextChoices):
    ADMIN = "admin", "Admin"
    CLIENT = "client", "Client"
    MASTER = "master", "Master"


class GenderType(models.TextChoices):
    MALE = "male", "Male"
    FEMALE = "female", "Female"


class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Phone number is required")

        phone_number = phone_number.strip().replace(" ", "")
        email = extra_fields.get("email")
        if email:
            extra_fields["email"] = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)

        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("user_type", UserType.ADMIN)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^\+?[1-9]\d{8,14}$",
                message="Phone number must be valid",
            )
        ],
    )
    email = models.EmailField(unique=True, null=True, blank=True, db_index=True)
    user_type = models.CharField(
        max_length=10,
        choices=UserType.choices,
        default=UserType.CLIENT,
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["phone_number"]),
            models.Index(fields=["email"]),
            models.Index(fields=["user_type"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["is_verified"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return self.phone_number

    @property
    def is_admin_role(self):
        return self.user_type == UserType.ADMIN

    @property
    def is_client(self):
        return self.user_type == UserType.CLIENT

    @property
    def is_master(self):
        return self.user_type == UserType.MASTER


class UserProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    first_name = models.CharField(max_length=100, blank=True, default="")
    last_name = models.CharField(max_length=100, blank=True, default="")
    avatar = models.ImageField(upload_to="users/avatars/", blank=True, null=True)
    gender = models.CharField(
        max_length=10,
        choices=GenderType.choices,
        blank=True,
        null=True,
    )
    bio = models.TextField(blank=True, default="")
    birth_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["gender"]),
            models.Index(fields=["created_at"]),
        ]

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def __str__(self):
        return f"{self.user.phone_number} profile"


def generate_otp():
    return str(random.randint(100000, 999999))


def otp_expiry():
    return timezone.now() + timedelta(minutes=5)


class UserOTP(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="otps",
    )
    code = models.CharField(
        max_length=6,
        validators=[
            RegexValidator(
                regex=r"^\d{6}$",
                message="OTP must contain 6 digits",
            )
        ],
    )
    attempts = models.PositiveSmallIntegerField(default=0)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField(default=otp_expiry)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "code"],
                name="unique_user_otp_code",
            )
        ]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["code"]),
            models.Index(fields=["is_used"]),
            models.Index(fields=["expires_at"]),
            models.Index(fields=["created_at"]),
        ]

    def save(self, *args, **kwargs):
        if not self.pk and not self.code:
            self.code = generate_otp()
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() >= self.expires_at

    def is_valid(self):
        return not self.is_used and not self.is_expired()

    def mark_used(self):
        if not self.is_used:
            self.is_used = True
            self.save(update_fields=["is_used"])

    def __str__(self):
        return f"{self.user.phone_number} - {self.code}"
