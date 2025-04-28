from django.urls import path
from .views import (
    RegisterView, 
    CustomLoginView, 
    CustomLogoutView,
    ProfileView,
    profile_update,
    reset_quiz_progress
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/update/', profile_update, name='profile_update'),
    path('profile/reset-quiz/<uuid:topic_id>/', reset_quiz_progress, name='reset_quiz'),
]