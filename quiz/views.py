from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.db.models import Count, Q, Sum, Case, When, IntegerField, F
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from datetime import timedelta
import random

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
        return redirect('quiz_results', topic_id=topic.id)
    
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
                next_url = reverse_lazy('quiz_question', kwargs={
                    'topic_id': topic.id, 
                    'question_id': next_question.id
                }) if next_question else reverse_lazy('quiz_results', kwargs={'topic_id': topic.id})
                
                return JsonResponse({
                    'success': True,
                    'is_correct': answer.is_correct,
                    'correct_option': question.correct_option,
                    'explanation': question.explanation,
                    'next_url': next_url
                })
            
            next_question = _get_next_question(request.user, topic)
            
            if not next_question:
                return redirect('quiz_results', topic_id=topic.id)
            
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


@login_required
def quiz_results(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    
    user_answers = UserAnswer.objects.filter(
        user=request.user,
        question__topic=topic
    ).select_related('question')
    
    total_questions = Question.objects.filter(topic=topic).count()
    answered_questions = user_answers.values('question').distinct().count()
    correct_answers = user_answers.filter(is_correct=True).count()
    incorrect_answers = answered_questions - correct_answers
    
    if answered_questions > 0:
        percentage_score = round((correct_answers / answered_questions) * 100)
    else:
        percentage_score = 0
    
    related_topics = Topic.objects.exclude(id=topic_id).annotate(
        questions_count=Count('questions')
    ).order_by('?')[:3]  
    
    context = {
        'topic': topic,
        'user_answers': user_answers,
        'total_questions': total_questions,
        'answered_questions': answered_questions,
        'correct_answers': correct_answers,
        'incorrect_answers': incorrect_answers,
        'percentage_score': percentage_score,
        'related_topics': related_topics,
    }
    
    return render(request, 'quiz/result_quiz.html', context)


@login_required
def leaderboard(request):
    filter_type = request.GET.get('filter', 'overall')
    topic_id = request.GET.get('topic')
    
    user_answers_query = UserAnswer.objects.all()
    
    if filter_type == 'weekly':
        week_ago = timezone.now() - timedelta(days=7)
        user_answers_query = user_answers_query.filter(created_at__gte=week_ago)
    elif filter_type == 'monthly':
        month_ago = timezone.now() - timedelta(days=30)
        user_answers_query = user_answers_query.filter(created_at__gte=month_ago)
    elif filter_type == 'topics' and topic_id:
        user_answers_query = user_answers_query.filter(question__topic_id=topic_id)
    
    users_stats = []
    
    users = User.objects.filter(is_active=True).distinct()
    for user in users:
        user_answers = user_answers_query.filter(user=user)
        correct_count = user_answers.filter(is_correct=True).count()
        total_count = user_answers.count()
        
        if total_count == 0:
            continue
        
        success_rate = (correct_count / total_count * 100) if total_count > 0 else 0
        points = correct_count * 10 - (total_count - correct_count) * 2  
        
        users_stats.append({
            'user': user,
            'correct_answers': correct_count,
            'total_answers': total_count,
            'success_rate': success_rate,
            'points': points
        })
    
    users_stats.sort(key=lambda x: x['points'], reverse=True)
    
    user_position = None
    total_users = len(users_stats)
    
    if request.user.is_authenticated:
        for index, stats in enumerate(users_stats):
            if stats['user'] == request.user:
                user_position = index + 1
                break
    
    paginator = Paginator(users_stats, 10) 
    page = request.GET.get('page')
    leaderboard = paginator.get_page(page)
    
    topics = Topic.objects.all()
    
    context = {
        'leaderboard': leaderboard,
        'filter_type': filter_type,
        'selected_topic': topic_id,
        'topics': topics,
        'user_position': user_position,
        'total_users': total_users
    }
    
    return render(request, 'quiz/leader_list.html', context)


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