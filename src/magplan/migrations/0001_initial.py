# Generated by Django 3.1.2 on 2020-11-15 11:40

import datetime
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Attachment",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "_old_id",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                (
                    "type",
                    models.SmallIntegerField(
                        choices=[(0, "Image"), (1, "PDF"), (2, "File")],
                        default=0,
                    ),
                ),
                ("original_filename", models.CharField(max_length=255)),
                (
                    "file",
                    models.FileField(
                        max_length=2048, upload_to="attachments/%Y/%m/%d/"
                    ),
                ),
                (
                    "meta",
                    django.contrib.postgres.fields.jsonb.JSONField(
                        default=dict
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Comment",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "_old_id",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                ("text", models.TextField(blank=True)),
                (
                    "type",
                    models.SmallIntegerField(
                        choices=[
                            (5, "system"),
                            (10, "private"),
                            (15, "public"),
                        ],
                        default=10,
                    ),
                ),
                ("object_id", models.PositiveIntegerField()),
                (
                    "meta",
                    django.contrib.postgres.fields.jsonb.JSONField(
                        default=dict
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Idea",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "_old_id",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                (
                    "title",
                    models.CharField(max_length=255, verbose_name="Заголовок"),
                ),
                ("description", models.TextField(verbose_name="Описание")),
                ("approved", models.BooleanField(null=True)),
                (
                    "author_type",
                    models.CharField(
                        choices=[
                            ("NO", "Нет автора"),
                            ("NW", "Новый автор"),
                            ("EX", "Существующий автор(ы)"),
                        ],
                        default="NO",
                        max_length=2,
                        verbose_name="Автор",
                    ),
                ),
                (
                    "authors_new",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Новые автор",
                    ),
                ),
            ],
            options={
                "permissions": (
                    (
                        "edit_extended_idea_attrs",
                        "Edit extended Idea attributes",
                    ),
                    (
                        "recieve_idea_email_updates",
                        "Recieve email updates for Idea",
                    ),
                ),
            },
        ),
        migrations.CreateModel(
            name="Issue",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "_old_id",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                ("number", models.SmallIntegerField(default=0)),
                ("title", models.CharField(max_length=255, null=True)),
                ("description", models.TextField(null=True)),
                (
                    "published_at",
                    models.DateField(default=datetime.date.today),
                ),
            ],
            options={
                "ordering": ["-number"],
            },
        ),
        migrations.CreateModel(
            name="Magazine",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "_old_id",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                ("slug", models.SlugField(max_length=255)),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Post",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "_old_id",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                (
                    "format",
                    models.SmallIntegerField(
                        choices=[(0, "Default"), (1, "Featured")], default=0
                    ),
                ),
                (
                    "finished_at",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        verbose_name="Дедлайн",
                    ),
                ),
                (
                    "published_at",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="Дата публикации"
                    ),
                ),
                (
                    "kicker",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "slug",
                    models.SlugField(blank=True, max_length=255, null=True),
                ),
                (
                    "title",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Заголовок статьи",
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True, verbose_name="Описание статьи"
                    ),
                ),
                ("views", models.IntegerField(default=0)),
                ("is_paywalled", models.BooleanField(default=False)),
                ("xmd", models.TextField(null=True)),
                ("html", models.TextField(null=True)),
                (
                    "meta",
                    django.contrib.postgres.fields.jsonb.JSONField(
                        default=dict
                    ),
                ),
                ("is_locked", models.BooleanField(default=False)),
                (
                    "css",
                    models.TextField(
                        blank=True,
                        help_text="CSS, который будет применяться к превью статьи",
                        null=True,
                        verbose_name="CSS-стили для статьи",
                    ),
                ),
            ],
            options={
                "permissions": (
                    (
                        "recieve_post_email_updates",
                        "Recieve email updates for Post",
                    ),
                    (
                        "edit_extended_post_attrs",
                        "Edit extended Post attributes",
                    ),
                ),
            },
        ),
        migrations.CreateModel(
            name="Postype",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "_old_id",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                ("slug", models.SlugField(max_length=255)),
                ("title", models.CharField(max_length=255)),
                (
                    "meta",
                    django.contrib.postgres.fields.jsonb.JSONField(
                        default=dict
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Profile",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "_old_id",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                ("is_public", models.BooleanField(default=False)),
                (
                    "f_name",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Имя",
                    ),
                ),
                (
                    "m_name",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Отчество",
                    ),
                ),
                (
                    "l_name",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Фамилия",
                    ),
                ),
                (
                    "n_name",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Ник",
                    ),
                ),
                (
                    "country",
                    models.SmallIntegerField(
                        choices=[
                            (0, "Россия"),
                            (1, "Украина"),
                            (2, "Беларусь"),
                            (3, "Казахстан"),
                        ],
                        default=0,
                        verbose_name="Страна",
                    ),
                ),
                (
                    "city",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="Город или поселок",
                    ),
                ),
                (
                    "notes",
                    models.TextField(
                        blank=True, null=True, verbose_name="Примечания"
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Section",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "_old_id",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                ("slug", models.SlugField(max_length=255)),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField(null=True)),
                ("sort", models.SmallIntegerField(default=0)),
                ("color", models.CharField(default="000000", max_length=6)),
                ("is_archived", models.BooleanField(default=False)),
                ("is_whitelisted", models.BooleanField(default=False)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Stage",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "_old_id",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                ("slug", models.SlugField(max_length=255)),
                ("title", models.CharField(max_length=255)),
                ("sort", models.SmallIntegerField(default=0)),
                (
                    "duration",
                    models.SmallIntegerField(blank=True, default=1, null=True),
                ),
                ("skip_notification", models.BooleanField(default=False)),
                (
                    "meta",
                    django.contrib.postgres.fields.jsonb.JSONField(
                        default=dict
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
