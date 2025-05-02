from django.urls import path
from . import views

app_name = 'chatbot'  # Nom de l'application pour le namespace

urlpatterns = [
    path('', views.chatbot, name='chatbot'),
    path('clear_history/', views.clear_history, name='clear_history'),
    path('toggle_history/', views.toggle_history, name='toggle_history'),
]