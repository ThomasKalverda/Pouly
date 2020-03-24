from django.urls import path, include
from . import views
from .views import PouleListView, PouleCreateView
from poule.views import TeamUpdateView

urlpatterns = [
    path('', PouleListView.as_view(), name='lobby-home'),
    path('poule/new/', PouleCreateView.as_view(), name='poule-create'),
    path('team/<int:pk>/update/', TeamUpdateView.as_view(), name='team-update')


]
