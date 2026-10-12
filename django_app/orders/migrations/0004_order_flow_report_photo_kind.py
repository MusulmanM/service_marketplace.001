import django.db.models.deletion
from decimal import Decimal
from django.db import migrations, models


def migrate_statuses_forward(apps, schema_editor):
    Order = apps.get_model("orders", "Order")
    Order.objects.filter(status="pending").update(status="new")


def migrate_statuses_backward(apps, schema_editor):
    Order = apps.get_model("orders", "Order")
    Order.objects.filter(status="new").update(status="pending")
    Order.objects.filter(status__in=["en_route", "on_site"]).update(status="accepted")


def copy_photo_type_to_kind(apps, schema_editor):
    # No-op if column rename handled by AlterField; kept for safety on fresh DBs
    pass


def copy_report_text_to_summary(apps, schema_editor):
    OrderReport = apps.get_model("orders", "OrderReport")
    for report in OrderReport.objects.all():
        text = getattr(report, "text", None) or ""
        if hasattr(report, "summary") and not report.summary and text:
            report.summary = text
            report.save(update_fields=["summary"])


def assign_order_numbers(apps, schema_editor):
    Order = apps.get_model("orders", "Order")
    seq = 1
    for order in Order.objects.order_by("created_at"):
        order.number_seq = seq
        order.save(update_fields=["number_seq"])
        seq += 1


class Migration(migrations.Migration):

    dependencies = [
        ("orders", "0003_alter_order_client_alter_order_status_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="number_seq",
            field=models.PositiveIntegerField(blank=True, editable=False, null=True, unique=True),
        ),
        migrations.RunPython(assign_order_numbers, migrations.RunPython.noop),
        migrations.RunPython(migrate_statuses_forward, migrate_statuses_backward),
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[
                    ("new", "New"),
                    ("accepted", "Accepted"),
                    ("en_route", "En route"),
                    ("on_site", "On site"),
                    ("in_progress", "In progress"),
                    ("completed", "Completed"),
                    ("cancelled", "Cancelled"),
                    ("rejected", "Rejected"),
                ],
                default="new",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="price",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddIndex(
            model_name="order",
            index=models.Index(fields=["number_seq"], name="orders_orde_number__9c0e1a_idx"),
        ),
        # Photo: rename photo_type → kind
        migrations.RemoveIndex(
            model_name="orderphoto",
            name="orders_orde_order_i_6003dc_idx",
        ),
        migrations.RenameField(
            model_name="orderphoto",
            old_name="photo_type",
            new_name="kind",
        ),
        migrations.AddIndex(
            model_name="orderphoto",
            index=models.Index(fields=["order", "kind"], name="orders_orde_order_i_kind_idx"),
        ),
        # Report: text → summary + invoice fields
        migrations.RenameField(
            model_name="orderreport",
            old_name="text",
            new_name="summary",
        ),
        migrations.AddField(
            model_name="orderreport",
            name="labor_cost",
            field=models.DecimalField(decimal_places=2, default=Decimal("0"), max_digits=12),
        ),
        migrations.AddField(
            model_name="orderreport",
            name="parts_cost",
            field=models.DecimalField(decimal_places=2, default=Decimal("0"), max_digits=12),
        ),
        migrations.AddField(
            model_name="orderreport",
            name="total",
            field=models.DecimalField(decimal_places=2, default=Decimal("0"), max_digits=12),
        ),
        migrations.AddField(
            model_name="orderreport",
            name="warranty_days",
            field=models.PositiveIntegerField(default=30),
        ),
        migrations.RunPython(copy_report_text_to_summary, migrations.RunPython.noop),
    ]
