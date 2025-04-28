from django.db import models
from django.contrib.auth.models import User
import uuid


class Topic(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, verbose_name="Название темы")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    image = models.ImageField(upload_to='topics/', blank=True, null=True, verbose_name="Изображение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    class Meta:
        verbose_name = "Тема"
        verbose_name_plural = "Темы"
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title
    
    def get_questions_count(self):
        return self.questions.count()
    
    def get_completed_count(self, user):
        return UserAnswer.objects.filter(question__topic=self, user=user).distinct().count()


class Question(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='questions', verbose_name="Тема")
    text = models.TextField(verbose_name="Текст вопроса")
    option1 = models.CharField(max_length=255, verbose_name="Вариант 1")
    option2 = models.CharField(max_length=255, verbose_name="Вариант 2")
    option3 = models.CharField(max_length=255, verbose_name="Вариант 3")
    option4 = models.CharField(max_length=255, verbose_name="Вариант 4")
    correct_option = models.IntegerField(choices=[(1, "Вариант 1"), (2, "Вариант 2"), (3, "Вариант 3"), (4, "Вариант 4")], 
                                         verbose_name="Правильный вариант")
    explanation = models.TextField(blank=True, null=True, verbose_name="Объяснение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"
        ordering = ['topic', 'created_at']
        
    def __str__(self):
        return f"{self.topic.title}: {self.text[:50]}..."
    
    def get_correct_option_text(self):
        if self.correct_option == 1:
            return self.option1
        elif self.correct_option == 2:
            return self.option2
        elif self.correct_option == 3:
            return self.option3
        else:
            return self.option4


class UserAnswer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers', verbose_name="Пользователь")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='user_answers', verbose_name="Вопрос")
    selected_option = models.IntegerField(choices=[(1, "Вариант 1"), (2, "Вариант 2"), (3, "Вариант 3"), (4, "Вариант 4")], 
                                          verbose_name="Выбранный вариант")
    is_correct = models.BooleanField(default=False, verbose_name="Правильно")
    answered_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата ответа")
    
    class Meta:
        verbose_name = "Ответ пользователя"
        verbose_name_plural = "Ответы пользователей"
        ordering = ['-answered_at']
        unique_together = ['user', 'question']
        
    def __str__(self):
        return f"{self.user.username} - {self.question.text[:30]}... - {'Правильно' if self.is_correct else 'Неправильно'}"
    
    def save(self, *args, **kwargs):
        self.is_correct = (self.selected_option == self.question.correct_option)
        super().save(*args, **kwargs)