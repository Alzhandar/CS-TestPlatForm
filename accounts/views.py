from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, UpdateView, TemplateView
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import RegisterForm, CustomLoginForm, ProfileUpdateForm, UserUpdateForm
from .models import Profile
from quiz.models import UserAnswer


class RegisterView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Аккаунт успешно создан, теперь вы можете войти!')
        return response


class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wrong_answers = UserAnswer.objects.filter(
            user=self.request.user, 
            is_correct=False
        ).select_related('question', 'question__topic').order_by('question__topic')
        
        topic_stats = {}
        for answer in UserAnswer.objects.filter(user=self.request.user).select_related('question__topic'):
            topic_name = answer.question.topic.title
            if topic_name not in topic_stats:
                topic_stats[topic_name] = {'correct': 0, 'incorrect': 0, 'total': 0}
            topic_stats[topic_name]['total'] += 1
            if answer.is_correct:
                topic_stats[topic_name]['correct'] += 1
            else:
                topic_stats[topic_name]['incorrect'] += 1
        
        for topic in topic_stats:
            total = topic_stats[topic]['total']
            if total > 0:
                topic_stats[topic]['percentage'] = (topic_stats[topic]['correct'] / total) * 100
            else:
                topic_stats[topic]['percentage'] = 0
        
        context.update({
            'wrong_answers': wrong_answers,
            'topic_stats': topic_stats,
        })
        return context


@login_required
def profile_update(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Ваш профиль успешно обновлен!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
        
    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'accounts/profile_update.html', context)


@login_required
def reset_quiz_progress(request, topic_id):
    UserAnswer.objects.filter(
        user=request.user,
        question__topic_id=topic_id
    ).delete()
    messages.success(request, 'Прогресс по тесту успешно сброшен!')
    return redirect('profile')