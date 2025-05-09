# Generated by Django 5.1.6 on 2025-04-28 10:38

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Topic",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "title",
                    models.CharField(max_length=255, verbose_name="Название темы"),
                ),
                (
                    "description",
                    models.TextField(blank=True, null=True, verbose_name="Описание"),
                ),
                (
                    "image",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="topics/",
                        verbose_name="Изображение",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата создания"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Дата обновления"),
                ),
            ],
            options={
                "verbose_name": "Тема",
                "verbose_name_plural": "Темы",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Question",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("text", models.TextField(verbose_name="Текст вопроса")),
                ("option1", models.CharField(max_length=255, verbose_name="Вариант 1")),
                ("option2", models.CharField(max_length=255, verbose_name="Вариант 2")),
                ("option3", models.CharField(max_length=255, verbose_name="Вариант 3")),
                ("option4", models.CharField(max_length=255, verbose_name="Вариант 4")),
                (
                    "correct_option",
                    models.IntegerField(
                        choices=[
                            (1, "Вариант 1"),
                            (2, "Вариант 2"),
                            (3, "Вариант 3"),
                            (4, "Вариант 4"),
                        ],
                        verbose_name="Правильный вариант",
                    ),
                ),
                (
                    "explanation",
                    models.TextField(blank=True, null=True, verbose_name="Объяснение"),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата создания"
                    ),
                ),
                (
                    "topic",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="questions",
                        to="quiz.topic",
                        verbose_name="Тема",
                    ),
                ),
            ],
            options={
                "verbose_name": "Вопрос",
                "verbose_name_plural": "Вопросы",
                "ordering": ["topic", "created_at"],
            },
        ),
        migrations.CreateModel(
            name="UserAnswer",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "selected_option",
                    models.IntegerField(
                        choices=[
                            (1, "Вариант 1"),
                            (2, "Вариант 2"),
                            (3, "Вариант 3"),
                            (4, "Вариант 4"),
                        ],
                        verbose_name="Выбранный вариант",
                    ),
                ),
                (
                    "is_correct",
                    models.BooleanField(default=False, verbose_name="Правильно"),
                ),
                (
                    "answered_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="Дата ответа"),
                ),
                (
                    "question",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_answers",
                        to="quiz.question",
                        verbose_name="Вопрос",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="answers",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ответ пользователя",
                "verbose_name_plural": "Ответы пользователей",
                "ordering": ["-answered_at"],
                "unique_together": {("user", "question")},
            },
        ),
    ]
