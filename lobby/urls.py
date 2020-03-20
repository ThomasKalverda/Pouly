from django.urls import path, include
from . import views
from .views import PouleListView

urlpatterns = [
    path('', PouleListView.as_view(), name='lobby-home'),


]
