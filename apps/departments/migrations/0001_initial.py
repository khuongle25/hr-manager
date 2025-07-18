# Generated by Django 4.2.7 on 2025-06-28 18:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Department",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True)),
                (
                    "lead",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="lead_departments",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "members",
                    models.ManyToManyField(
                        related_name="departments", to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="LeaveType",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=50)),
                ("description", models.TextField(blank=True)),
                ("max_days_per_year", models.PositiveIntegerField(default=12)),
            ],
        ),
        migrations.CreateModel(
            name="LeaveRequest",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("reason", models.TextField()),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("approved", "Approved"),
                            ("denied", "Denied"),
                        ],
                        default="pending",
                        max_length=10,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "approver",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="approved_leaves",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "department",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="departments.department",
                    ),
                ),
                (
                    "employee",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="leave_requests",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "leave_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="departments.leavetype",
                    ),
                ),
            ],
        ),
    ]
