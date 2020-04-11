from django.urls import path
from .views import PouleListView, PouleCreateView


urlpatterns = [
    path('', PouleListView.as_view(), name='lobby-home'),
    path('poule/new/', PouleCreateView.as_view(), name='poule-create'),
]
