from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid


class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="Пользователь")
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png', verbose_name="Аватар")
    bio = models.TextField(max_length=500, blank=True, verbose_name="О себе")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"
        
    def __str__(self):
        return f"Профиль пользователя {self.user.username}"
    
    def get_total_questions_answered(self):
        return self.user.answers.count()
    
    def get_correct_answers_count(self):
        return self.user.answers.filter(is_correct=True).count()
    
    def get_incorrect_answers_count(self):
        return self.user.answers.filter(is_correct=False).count()
    
    def get_success_rate(self):
        total = self.get_total_questions_answered()
        if total > 0:
            return (self.get_correct_answers_count() / total) * 100
        return 0


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()