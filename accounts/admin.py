from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Профили'
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_total_questions_answered', 'get_correct_answers_count', 
                   'get_incorrect_answers_count', 'get_success_rate_display')
    search_fields = ('user__username', 'user__email', 'bio')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('user', 'created_at', 'updated_at')
    
    def get_success_rate_display(self, obj):
        return f"{obj.get_success_rate():.1f}%"
    get_success_rate_display.short_description = 'Процент успеха'