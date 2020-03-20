from django.urls import path
from . import views

urlpatterns = [
    path('', views.overview, name='poule-overview'),
    path('ranking/', views.ranking, name='poule-ranking'),
    path('predictions/', views.predictions, name='poule-predictions'),
    path('teams/', views.teams, name='poule-teams'),
    path('info/', views.info, name='poule-info'),
    path('games/', views.games, name='poule-games'),
    path('rules/', views.rules, name='poule-rules'),
]
