from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('topic/<uuid:topic_id>/', views.topic_detail, name='topic_detail'),
    path('topic/<uuid:topic_id>/start/', views.start_quiz, name='start_quiz'),
    path('topic/<uuid:topic_id>/question/<uuid:question_id>/', views.quiz_question, name='quiz_question'),
]