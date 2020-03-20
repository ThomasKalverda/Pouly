from django.shortcuts import render
from django.views.generic import ListView, DetailView, DeleteView
from .models import Poule
from django.http import HttpResponse


def home(request):
    context = {
        'poules': Poule.objects.all()
    }
    return render(request, 'lobby/home.html', context)


class PouleListView(ListView):
    model = Poule
    template_name = 'lobby/home.html'
    context_object_name = 'poules'







