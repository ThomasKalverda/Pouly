from django.shortcuts import render
from django.views.generic import ListView, DetailView, DeleteView, CreateView, UpdateView
from .models import Poule
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin


def home(request):
    context = {
        'poules': Poule.objects.all()
    }
    return render(request, 'lobby/home.html', context)


class PouleListView(ListView):
    model = Poule
    template_name = 'lobby/home.html'
    context_object_name = 'poules'


class PouleCreateView(LoginRequiredMixin, CreateView):
    model = Poule
    template_name = 'lobby/poule_form.html'
    fields = ['name', 'description', 'image', 'sport']

    def form_valid(self, form):
        form.instance.admin = self.request.user
        return super().form_valid(form)




