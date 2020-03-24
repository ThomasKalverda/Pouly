from django.urls import path
from . import views
from .views import PouleOverviewView, PouleGamesView, PouleInfoView, PoulePredictionsView, PouleRankingView, PouleRulesView, PouleTeamsView, PouleDeleteView

urlpatterns = [
    path('overview/', PouleOverviewView.as_view(), name='poule-overview'),
    path('ranking/', PouleRankingView.as_view(), name='poule-ranking'),
    path('predictions/', PoulePredictionsView.as_view(), name='poule-predictions'),
    path('rules/', PouleRulesView.as_view(), name='poule-rules'),
    path('games/', PouleGamesView.as_view(), name='poule-games'),
    path('teams/', PouleTeamsView.as_view(), name='poule-teams'),
    path('info/', PouleInfoView.as_view(), name='poule-info'),
    path('delete/', PouleDeleteView.as_view(), name='poule-delete')
]
