from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.db.models import Count, Q
from django.contrib import messages
import random
from django.urls import reverse, reverse_lazy

from .models import Topic, Question, UserAnswer
from .forms import UserAnswerForm


class HomeView(LoginRequiredMixin, ListView):
    model = Topic
    template_name = 'quiz/home.html'
    context_object_name = 'topics'
    
    def get_queryset(self):
        queryset = Topic.objects.all().annotate(questions_count=Count('questions'))
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        for topic in context['topics']:
            user_answers = UserAnswer.objects.filter(
                user=user,
                question__topic=topic
            )
            answered_questions = user_answers.values('question').distinct().count()
            if topic.questions_count > 0:
                topic.progress = (answered_questions / topic.questions_count) * 100
            else:
                topic.progress = 0
            topic.correct_answers = user_answers.filter(is_correct=True).count()
            
        return context


@login_required
def topic_detail(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    
    user_answers = UserAnswer.objects.filter(
        user=request.user,
        question__topic=topic
    )
    total_questions = Question.objects.filter(topic=topic).count()
    answered_questions = user_answers.values('question').distinct().count()
    correct_answers = user_answers.filter(is_correct=True).count()
    
    progress = (answered_questions / total_questions) * 100 if total_questions > 0 else 0
    
    accuracy = (correct_answers / answered_questions) * 100 if answered_questions > 0 else 0
    
    context = {
        'topic': topic,
        'total_questions': total_questions,
        'answered_questions': answered_questions,
        'correct_answers': correct_answers,
        'progress': progress,
        'accuracy': accuracy,
    }
    
    return render(request, 'quiz/topic_detail.html', context)


@login_required
def start_quiz(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    questions = Question.objects.filter(topic=topic)
    
    if not questions:
        messages.warning(request, f'По теме "{topic.title}" пока нет вопросов.')
        return redirect('home')
    
    answered_correctly = UserAnswer.objects.filter(
        user=request.user,
        question__topic=topic,
        is_correct=True
    ).values_list('question_id', flat=True)
    
    unanswered_questions = questions.exclude(id__in=answered_correctly)
    
    if not unanswered_questions:
        messages.success(
            request, 
            f'Поздравляем! Вы правильно ответили на все вопросы темы "{topic.title}". '
            f'Вы можете сбросить прогресс и начать заново.'
        )
        return redirect('topic_detail', topic_id=topic.id)
    
    question = random.choice(list(unanswered_questions))
    
    return redirect('quiz_question', topic_id=topic.id, question_id=question.id)


@login_required
def quiz_question(request, topic_id, question_id):
    topic = get_object_or_404(Topic, id=topic_id)
    question = get_object_or_404(Question, id=question_id, topic=topic)
    
    try:
        user_answer = UserAnswer.objects.get(user=request.user, question=question)
        previous_answer = user_answer.selected_option
    except UserAnswer.DoesNotExist:
        previous_answer = None
        user_answer = None
    
    if request.method == 'POST':
        form = UserAnswerForm(request.POST, question=question, instance=user_answer)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.user = request.user
            answer.question = question
            answer.is_correct = (answer.selected_option == question.correct_option)
            answer.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                next_question = _get_next_question(request.user, topic)
                # Заменить reverse_lazy на str(reverse())
                next_url = reverse('quiz_question', kwargs={
                    'topic_id': topic.id, 
                    'question_id': next_question.id
                }) if next_question else None
                
                return JsonResponse({
                    'success': True,
                    'is_correct': answer.is_correct,
                    'correct_option': question.correct_option,
                    'explanation': question.explanation,
                    'next_url': next_url
                })
            
            
            next_question = _get_next_question(request.user, topic)
            
            if not next_question:
                messages.success(
                    request, 
                    f'Поздравляем! Вы завершили все вопросы темы "{topic.title}".'
                )
                return redirect('topic_detail', topic_id=topic.id)
            
            return redirect('quiz_question', topic_id=topic.id, question_id=next_question.id)
    else:
        form = UserAnswerForm(question=question, instance=user_answer)
    
    total_questions = Question.objects.filter(topic=topic).count()
    answered_questions = UserAnswer.objects.filter(
        user=request.user,
        question__topic=topic
    ).values('question').distinct().count()
    
    progress = int((answered_questions / total_questions) * 100) if total_questions > 0 else 0
    
    context = {
        'topic': topic,
        'question': question,
        'form': form,
        'previous_answer': previous_answer,
        'progress': progress,
        'total_questions': total_questions,
        'answered_questions': answered_questions,
    }
    
    return render(request, 'quiz/quiz_question.html', context)


def _get_next_question(user, topic):
    questions = Question.objects.filter(topic=topic)
    
    answered_correctly = UserAnswer.objects.filter(
        user=user,
        question__topic=topic,
        is_correct=True
    ).values_list('question_id', flat=True)
    
    unanswered_questions = questions.exclude(id__in=answered_correctly)
    
    if unanswered_questions:
        return random.choice(list(unanswered_questions))
    return None