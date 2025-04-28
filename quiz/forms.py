from django import forms
from .models import Topic, Question, UserAnswer


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ['title', 'description', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['topic', 'text', 'option1', 'option2', 'option3', 'option4', 'correct_option', 'explanation']
        widgets = {
            'topic': forms.Select(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'option1': forms.TextInput(attrs={'class': 'form-control'}),
            'option2': forms.TextInput(attrs={'class': 'form-control'}),
            'option3': forms.TextInput(attrs={'class': 'form-control'}),
            'option4': forms.TextInput(attrs={'class': 'form-control'}),
            'correct_option': forms.Select(attrs={'class': 'form-control'}),
            'explanation': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class UserAnswerForm(forms.ModelForm):
    class Meta:
        model = UserAnswer
        fields = ['selected_option']
        widgets = {
            'selected_option': forms.RadioSelect()
        }

    def __init__(self, *args, question=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        if question:
            self.fields['selected_option'].choices = [
                (1, question.option1),
                (2, question.option2),
                (3, question.option3),
                (4, question.option4)
            ]
            self.question_id = question.id