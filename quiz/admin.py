from django.contrib import admin
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django import forms
import json
from .models import Topic, Question, UserAnswer
from django.utils.html import format_html
from django.urls import reverse

class ImportJsonForm(forms.Form):
    # Оставляем существующие поля
    json_file = forms.FileField(
        label="Выберите JSON файл", 
        required=False,
        help_text="Загрузите файл с вопросами в формате JSON"
    )
    topic = forms.ModelChoiceField(
        queryset=Topic.objects.all(),
        label="Выберите тему для импорта",
        required=True
    )
    # Добавляем поле для текстового ввода JSON
    json_text = forms.CharField(
        label="Или введите JSON напрямую",
        widget=forms.Textarea(attrs={
            'rows': 20,
            'cols': 80,
            'class': 'vLargeTextField',
            'style': 'font-family: monospace; resize: both;',
            'placeholder': '''[
    {
        "text": "Текст вопроса",
        "option1": "Вариант 1",
        "option2": "Вариант 2",
        "option3": "Вариант 3",
        "option4": "Вариант 4",
        "correct_option": 1,
        "explanation": "Объяснение (необязательно)"
    }
]'''
        }),
        required=False,
        help_text="Введите вопросы в формате JSON. Либо загрузите файл, либо введите текст."
    )
    
    def clean(self):
        cleaned_data = super().clean()
        json_file = cleaned_data.get('json_file')
        json_text = cleaned_data.get('json_text')
        
        if not json_file and not json_text:
            raise forms.ValidationError("Необходимо либо загрузить файл, либо ввести JSON текст")
            
        if json_file and json_text:
            raise forms.ValidationError("Выберите только один способ ввода данных: файл или текст")
        
        return cleaned_data

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'get_questions_count', 'created_at', 'updated_at', 'export_button')
    search_fields = ('title', 'description')
    list_filter = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    def get_questions_count(self, obj):
        return obj.questions.count()
    get_questions_count.short_description = 'Кол-во вопросов'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<uuid:topic_id>/export-json/', self.export_json_by_topic, name='export_json_by_topic'),
        ]
        return custom_urls + urls
    
    def export_json_by_topic(self, request, topic_id):
        topic = Topic.objects.get(pk=topic_id)
        questions = Question.objects.filter(topic=topic)
        questions_data = []
        
        for question in questions:
            questions_data.append({
                'text': question.text,
                'option1': question.option1,
                'option2': question.option2,
                'option3': question.option3,
                'option4': question.option4,
                'correct_option': question.correct_option,
                'explanation': question.explanation
            })
        
        response = HttpResponse(json.dumps(questions_data, ensure_ascii=False, indent=4), 
                                content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename={topic.title}_questions.json'
        return response
    
    def export_button(self, obj):
        """Добавляет кнопку экспорта JSON для каждой темы в списке"""
        return format_html(
            '<a class="button" href="{}">Экспорт JSON</a>',
            reverse('admin:export_json_by_topic', args=[obj.pk])
        )
    export_button.short_description = 'Экспорт'
    export_button.allow_tags = True


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'topic', 'correct_option', 'created_at', )
    list_filter = ('topic', 'created_at')
    search_fields = ('text', 'explanation')
    date_hierarchy = 'created_at'
    list_select_related = ('topic',)
    actions = ['export_as_json']
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-json/', self.import_json, name='import_json'),
        ]
        return custom_urls + urls
    
    def export_as_json(self, request, queryset):
        questions_data = []
        for question in queryset:
            questions_data.append({
                'text': question.text,
                'option1': question.option1,
                'option2': question.option2,
                'option3': question.option3,
                'option4': question.option4,
                'correct_option': question.correct_option,
                'explanation': question.explanation
            })
        
        response = HttpResponse(json.dumps(questions_data, ensure_ascii=False, indent=4), 
                                content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename=questions.json'
        return response
    export_as_json.short_description = "Экспортировать выбранные вопросы в JSON"
    
    def import_json(self, request):
        if request.method == 'POST':
            form = ImportJsonForm(request.POST, request.FILES)
            if form.is_valid():
                topic = form.cleaned_data['topic']
                json_file = form.cleaned_data['json_file']
                json_text = form.cleaned_data['json_text']
                
                try:
                    if json_file:
                        # Обработка файла (существующий код)
                        data = json.loads(json_file.read().decode('utf-8'))
                    else:
                        # Обработка текстового ввода
                        data = json.loads(json_text)
                    
                    imported_count = 0
                    errors_count = 0
                    
                    for item in data:
                        try:
                            if all(key in item for key in ['text', 'option1', 'option2', 'option3', 'option4', 'correct_option']):
                                Question.objects.create(
                                    topic=topic,
                                    text=item['text'],
                                    option1=item['option1'],
                                    option2=item['option2'],
                                    option3=item['option3'],
                                    option4=item['option4'],
                                    correct_option=item['correct_option'],
                                    explanation=item.get('explanation', '')
                                )
                                imported_count += 1
                            else:
                                errors_count += 1
                        except Exception as e:
                            errors_count += 1
                    
                    if errors_count > 0:
                        messages.warning(request, f'Импортировано {imported_count} вопросов, пропущено из-за ошибок: {errors_count}')
                    else:
                        messages.success(request, f'Успешно импортировано {imported_count} вопросов')
                    
                    return redirect('..')
                except json.JSONDecodeError as e:
                    line_col = f" (строка {e.lineno}, позиция {e.colno})" if hasattr(e, 'lineno') else ""
                    messages.error(request, f'Ошибка формата JSON{line_col}: {str(e)}')
                except Exception as e:
                    messages.error(request, f'Ошибка при импорте: {str(e)}')
        else:
            form = ImportJsonForm()
        
        return render(request, 'admin/quiz/import_json.html', {'form': form})
    
    def changelist_view(self, request, extra_context=None):
        """Добавляем кнопку импорта на страницу списка вопросов"""
        extra_context = extra_context or {}
        extra_context['import_button'] = format_html(
            '<a href="{}" class="button">Импортировать из JSON</a>',
            reverse('admin:import_json')
        )
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'selected_option', 'is_correct', 'answered_at')
    list_filter = ('is_correct', 'answered_at', 'question__topic')
    search_fields = ('user__username', 'question__text')
    date_hierarchy = 'answered_at'
    list_select_related = ('user', 'question', 'question__topic')
    
    def get_readonly_fields(self, request, obj=None):
        return ['user', 'question', 'selected_option', 'is_correct', 'answered_at']