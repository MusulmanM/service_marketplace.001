"""
Idempotent demo data seeder.

Usage:
    python manage.py seed_demo

Demo passwords: Demo1234!
Client phones: +998901000001 … +998901000010
Master phones: +998902000001 … +998902000010
"""

from __future__ import annotations

import io
import random
from decimal import Decimal
from datetime import timedelta

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.utils.text import slugify
from PIL import Image

from masters.models import MasterProfile, MasterService, ServiceCategory, ServiceCity
from orders.models import (
    Order,
    OrderPhoto,
    OrderPhotoKind,
    OrderReport,
    OrderReview,
    OrderStatus,
    OrderStatusHistory,
)
from users.models import User, UserProfile, UserType

DEMO_PASSWORD = "Demo1234!"
DEMO_TAG = "demo_seed"

CATEGORIES = [
    ("HVAC", "hvac", "Air conditioning and heating"),
    ("Electrical", "electrical", "Wiring, panels, outlets"),
    ("Plumbing", "plumbing", "Pipes, taps, drainage"),
    ("Appliance Repair", "appliance-repair", "Home appliances"),
    ("Cleaning", "cleaning", "Deep and AC cleaning"),
    ("Painting", "painting", "Interior painting"),
    ("Carpentry", "carpentry", "Furniture and doors"),
    ("Security", "security", "Cameras and alarms"),
    ("IT Support", "it-support", "Network and PC help"),
    ("Moving", "moving", "Local moving help"),
]

CITIES = [
    ("Yunusabad", "yunusabad"),
    ("Chilanzar", "chilanzar"),
    ("Mirzo-Ulugbek", "mirzo-ulugbek"),
    ("Yakkasaray", "yakkasaray"),
    ("Sergeli", "sergeli"),
    ("Shaykhontohur", "shaykhontohur"),
    ("Mirobod", "mirobod"),
    ("Uchtepa", "uchtepa"),
    ("Olmazor", "olmazor"),
    ("Bektemir", "bektemir"),
]

SERVICES = [
    ("AC Cleaning", "hvac", 250000),
    ("AC Installation", "hvac", 800000),
    ("Wiring Repair", "electrical", 180000),
    ("Panel Upgrade", "electrical", 450000),
    ("Outlet Installation", "electrical", 90000),
    ("Pipe Leak Fix", "plumbing", 150000),
    ("Washing Machine Repair", "appliance-repair", 220000),
    ("Fridge Diagnostics", "appliance-repair", 160000),
    ("Deep Cleaning", "cleaning", 350000),
    ("Door Lock Install", "security", 200000),
]

CLIENT_NAMES = [
    ("Aziza", "Karimova"),
    ("Dilshod", "Rakhimov"),
    ("Malika", "Tursunova"),
    ("Jasur", "Aliyev"),
    ("Nilufar", "Ismoilova"),
    ("Bekzod", "Nazarov"),
    ("Sevara", "Yusupova"),
    ("Otabek", "Khasanov"),
    ("Madina", "Saidova"),
    ("Sherzod", "Ergashev"),
]

MASTER_NAMES = [
    ("Akmal", "Usmonov"),
    ("Farrukh", "Qodirov"),
    ("Jamshid", "Abdullayev"),
    ("Rustam", "Sattorov"),
    ("Bahodir", "Mirzayev"),
    ("Sardor", "Toshmatov"),
    ("Ibrohim", "Rahmonov"),
    ("Nodir", "Ganiyev"),
    ("Ulugbek", "Sobirov"),
    ("Komil", "Zokirov"),
]

STREETS = [
    "Amir Temur ko'chasi",
    "Navoiy prospekti",
    "Shota Rustaveli",
    "Buyuk Ipak Yo'li",
    "Mustaqillik maydoni",
    "Bobur ko'chasi",
    "Farobiy ko'chasi",
    "Labzak",
    "Qatortol",
    "Beruniy",
]

ORDER_TITLES = [
    "AC not cooling",
    "Kitchen outlet sparking",
    "Bathroom pipe leak",
    "Washing machine won't spin",
    "Electrical panel upgrade",
    "Install new AC unit",
    "Deep clean after renovation",
    "Fridge making noise",
    "Replace door lock",
    "Rewire living room",
    "AC seasonal maintenance",
    "Fix hallway lighting",
]


def make_placeholder_image(label: str, color: tuple[int, int, int]) -> ContentFile:
    img = Image.new("RGB", (640, 480), color)
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    return ContentFile(buffer.getvalue(), name=f"{slugify(label)}.jpg")


class Command(BaseCommand):
    help = "Seed idempotent demo data (10 per category). Password: Demo1234!"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Remove previously seeded demo data before creating",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["clear"]:
            self._clear_demo()

        categories = self._seed_categories()
        cities = self._seed_cities()
        clients = self._seed_clients()
        masters = self._seed_masters(categories, cities)
        services = self._seed_services(masters, categories)
        orders = self._seed_orders(clients, masters, services, cities)
        photos = self._seed_photos(orders)
        reports = self._seed_reports(orders)
        reviews = self._seed_reviews(orders)

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Demo seed complete"))
        self.stdout.write(f"  Categories:     {len(categories)}")
        self.stdout.write(f"  Cities:         {len(cities)}")
        self.stdout.write(f"  Clients:        {len(clients)}")
        self.stdout.write(f"  Masters:        {len(masters)}")
        self.stdout.write(f"  Services:       {len(services)}")
        self.stdout.write(f"  Orders:         {len(orders)}")
        self.stdout.write(f"  Photos:         {photos}")
        self.stdout.write(f"  Reports:        {reports}")
        self.stdout.write(f"  Reviews:        {reviews}")
        self.stdout.write("")
        self.stdout.write("Login examples:")
        self.stdout.write(f"  Master: +998902000001 / {DEMO_PASSWORD}")
        self.stdout.write(f"  Client: +998901000001 / {DEMO_PASSWORD}")

    def _clear_demo(self):
        demo_phones = [f"+9989010000{i:02d}" for i in range(1, 11)] + [
            f"+9989020000{i:02d}" for i in range(1, 11)
        ]
        users = User.objects.filter(phone_number__in=demo_phones)
        Order.objects.filter(client__in=users).delete()
        Order.objects.filter(master__user__in=users).delete()
        MasterProfile.objects.filter(user__in=users).delete()
        users.delete()
        self.stdout.write(self.style.WARNING("Cleared previous demo users/orders"))

    def _seed_categories(self):
        items = []
        for name, slug, desc in CATEGORIES:
            obj, _ = ServiceCategory.objects.get_or_create(
                slug=slug,
                defaults={"name": name, "description": desc, "is_active": True},
            )
            if obj.name != name:
                obj.name = name
                obj.description = desc
                obj.is_active = True
                obj.save(update_fields=["name", "description", "is_active"])
            items.append(obj)
        return items

    def _seed_cities(self):
        items = []
        for name, slug in CITIES:
            obj, _ = ServiceCity.objects.get_or_create(
                slug=slug,
                defaults={"name": name, "is_active": True},
            )
            if obj.name != name:
                obj.name = name
                obj.is_active = True
                obj.save(update_fields=["name", "is_active"])
            items.append(obj)
        return items

    def _seed_clients(self):
        clients = []
        for i, (first, last) in enumerate(CLIENT_NAMES, start=1):
            phone = f"+9989010000{i:02d}"
            user, created = User.objects.get_or_create(
                phone_number=phone,
                defaults={
                    "user_type": UserType.CLIENT,
                    "is_active": True,
                    "is_verified": True,
                    "email": f"client{i:02d}@demo.local",
                },
            )
            if created or not user.check_password(DEMO_PASSWORD):
                user.set_password(DEMO_PASSWORD)
                user.user_type = UserType.CLIENT
                user.is_active = True
                user.is_verified = True
                user.save()
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.first_name = first
            profile.last_name = last
            profile.bio = DEMO_TAG
            profile.save()
            clients.append(user)
        return clients

    def _seed_masters(self, categories, cities):
        masters = []
        for i, (first, last) in enumerate(MASTER_NAMES, start=1):
            phone = f"+9989020000{i:02d}"
            user, created = User.objects.get_or_create(
                phone_number=phone,
                defaults={
                    "user_type": UserType.MASTER,
                    "is_active": True,
                    "is_verified": True,
                    "email": f"master{i:02d}@demo.local",
                },
            )
            if created or not user.check_password(DEMO_PASSWORD):
                user.set_password(DEMO_PASSWORD)
                user.user_type = UserType.MASTER
                user.is_active = True
                user.is_verified = True
                user.save()
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.first_name = first
            profile.last_name = last
            profile.bio = DEMO_TAG
            profile.save()

            city = cities[(i - 1) % len(cities)]
            master, _ = MasterProfile.objects.get_or_create(
                user=user,
                defaults={
                    "name": f"{first} {last}",
                    "title": categories[(i - 1) % len(categories)].name + " specialist",
                    "description": f"Experienced {categories[(i - 1) % len(categories)].name} master in Tashkent.",
                    "experience_years": 3 + (i % 8),
                    "rating": Decimal(str(round(4.2 + (i % 9) * 0.1, 2))),
                    "city": city.name,
                    "is_available": True,
                    "is_verified": True,
                },
            )
            master.name = f"{first} {last}"
            master.title = categories[(i - 1) % len(categories)].name + " specialist"
            master.description = f"Experienced {categories[(i - 1) % len(categories)].name} master in Tashkent."
            master.experience_years = 3 + (i % 8)
            master.rating = Decimal(str(round(4.2 + (i % 9) * 0.1, 2)))
            master.city = city.name
            master.is_available = True
            master.is_verified = True
            master.save()
            master.categories.set([categories[(i - 1) % len(categories)], categories[i % len(categories)]])
            master.cities.set([city, cities[i % len(cities)]])
            masters.append(master)
        return masters

    def _seed_services(self, masters, categories):
        cat_by_slug = {c.slug: c for c in categories}
        services = []
        for i, (title, cat_slug, price) in enumerate(SERVICES):
            master = masters[i % len(masters)]
            category = cat_by_slug[cat_slug]
            obj, _ = MasterService.objects.get_or_create(
                master=master,
                title=title,
                defaults={
                    "category": category,
                    "description": f"{title} in Tashkent — demo service",
                    "price": Decimal(price),
                    "duration_minutes": 60 + (i * 15) % 120,
                    "is_active": True,
                },
            )
            obj.category = category
            obj.price = Decimal(price)
            obj.is_active = True
            obj.save()
            services.append(obj)
        return services

    def _seed_orders(self, clients, masters, services, cities):
        statuses = [
            OrderStatus.NEW,
            OrderStatus.ACCEPTED,
            OrderStatus.EN_ROUTE,
            OrderStatus.ON_SITE,
            OrderStatus.IN_PROGRESS,
            OrderStatus.COMPLETED,
            OrderStatus.COMPLETED,
            OrderStatus.COMPLETED,
            OrderStatus.ACCEPTED,
            OrderStatus.IN_PROGRESS,
            OrderStatus.COMPLETED,
            OrderStatus.COMPLETED,
        ]
        # Prefer first master for easy login testing
        primary_master = masters[0]
        orders = []
        now = timezone.now()

        for i in range(12):
            client = clients[i % len(clients)]
            master = primary_master if i < 8 else masters[i % len(masters)]
            service = services[i % len(services)]
            city = cities[i % len(cities)]
            status = statuses[i]
            title = ORDER_TITLES[i % len(ORDER_TITLES)]
            address = f"{STREETS[i % len(STREETS)]} {10 + i}, {city.name}, Tashkent"
            price = service.price + Decimal(i * 15000)

            order = (
                Order.objects.filter(client=client, master=master, title=title, address=address)
                .order_by("created_at")
                .first()
            )
            if order is None:
                order = Order(
                    client=client,
                    master=master,
                    service=service,
                    title=title,
                    description=f"Demo order: {title}. Customer requests visit today.",
                    address=address,
                    price=price,
                    status=OrderStatus.NEW,
                    scheduled_at=now + timedelta(hours=2 + i),
                )
                order.save()
            else:
                order.service = service
                order.description = f"Demo order: {title}. Customer requests visit today."
                order.price = price
                order.scheduled_at = now + timedelta(hours=2 + i)
                order.save()

            # Apply status via history-friendly transitions from new
            self._force_status(order, status)
            orders.append(order)
        return orders

    def _force_status(self, order: Order, target: str):
        """Walk legal transitions to reach target, or set directly for demo."""
        path = {
            OrderStatus.NEW: [],
            OrderStatus.ACCEPTED: [OrderStatus.ACCEPTED],
            OrderStatus.EN_ROUTE: [OrderStatus.ACCEPTED, OrderStatus.EN_ROUTE],
            OrderStatus.ON_SITE: [OrderStatus.ACCEPTED, OrderStatus.EN_ROUTE, OrderStatus.ON_SITE],
            OrderStatus.IN_PROGRESS: [
                OrderStatus.ACCEPTED,
                OrderStatus.EN_ROUTE,
                OrderStatus.ON_SITE,
                OrderStatus.IN_PROGRESS,
            ],
            OrderStatus.COMPLETED: [
                OrderStatus.ACCEPTED,
                OrderStatus.EN_ROUTE,
                OrderStatus.ON_SITE,
                OrderStatus.IN_PROGRESS,
                OrderStatus.COMPLETED,
            ],
        }
        # Reset to new without invalid history noise when re-seeding
        if order.status != OrderStatus.NEW:
            OrderStatusHistory.objects.filter(order=order).delete()
            order.status = OrderStatus.NEW
            order.completed_at = None
            order.save(update_fields=["status", "completed_at", "updated_at"])

        for step in path.get(target, []):
            if order.status != step:
                order.set_status(step)

    def _seed_photos(self, orders):
        count = 0
        completed = [o for o in orders if o.status == OrderStatus.COMPLETED]
        in_progress = [o for o in orders if o.status == OrderStatus.IN_PROGRESS]
        targets = completed[:4] + in_progress[:2]
        colors = {
            OrderPhotoKind.BEFORE: (70, 90, 120),
            OrderPhotoKind.AFTER: (40, 140, 90),
        }
        for order in targets:
            for kind in (OrderPhotoKind.BEFORE, OrderPhotoKind.AFTER):
                exists = order.photos.filter(kind=kind).exists()
                if exists:
                    count += order.photos.filter(kind=kind).count()
                    continue
                photo = OrderPhoto(
                    order=order,
                    uploaded_by=order.master.user,
                    kind=kind,
                    caption=f"{kind} work — demo",
                )
                photo.image.save(
                    f"{order.number_seq}_{kind}.jpg",
                    make_placeholder_image(f"{kind}-{order.number_seq}", colors[kind]),
                    save=True,
                )
                count += 1
        return count

    def _seed_reports(self, orders):
        count = 0
        for order in orders:
            if order.status != OrderStatus.COMPLETED:
                continue
            labor = Decimal(order.price or 150000) * Decimal("0.7")
            parts = Decimal(order.price or 150000) * Decimal("0.3")
            report, created = OrderReport.objects.get_or_create(
                order=order,
                defaults={
                    "master": order.master,
                    "summary": f"Completed: {order.title}. Equipment tested and handed over to client.",
                    "labor_cost": labor.quantize(Decimal("1")),
                    "parts_cost": parts.quantize(Decimal("1")),
                    "total": (labor + parts).quantize(Decimal("1")),
                    "warranty_days": 30 + (count % 3) * 30,
                    "checklist": ["Diagnostics", "Repair", "Client sign-off"],
                },
            )
            if not created:
                report.summary = f"Completed: {order.title}. Equipment tested and handed over to client."
                report.labor_cost = labor.quantize(Decimal("1"))
                report.parts_cost = parts.quantize(Decimal("1"))
                report.total = (labor + parts).quantize(Decimal("1"))
                report.save()
            count += 1
        return count

    def _seed_reviews(self, orders):
        count = 0
        completed = [o for o in orders if o.status == OrderStatus.COMPLETED]
        for i, order in enumerate(completed[:8]):
            rating = 4 + (i % 2)
            review, created = OrderReview.objects.get_or_create(
                order=order,
                defaults={
                    "client": order.client,
                    "master": order.master,
                    "rating": rating,
                    "comment": random.choice(
                        [
                            "Great work, on time!",
                            "Professional and clean.",
                            "Fixed quickly, recommend.",
                            "Excellent service in Tashkent.",
                            "Will call again.",
                        ]
                    ),
                },
            )
            if not created and review.rating != rating:
                review.rating = rating
                review.save()
            count += 1
        return count
