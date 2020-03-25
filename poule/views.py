from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView, DetailView, DeleteView, UpdateView, View
from django.views.generic.detail import SingleObjectMixin

from lobby.models import Poule
from .models import Game, Team
from django.db.models.functions import TruncDay
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import FormMixin, FormView
from .forms import CreateTeamForm, CreateGameForm


class PouleOverviewView(DetailView):
    model = Poule
    template_name = 'poule/overview.html'


class PouleRankingView(DetailView):
    model = Poule
    template_name = 'poule/ranking.html'


class PoulePredictionsView(DetailView):
    model = Poule
    template_name = 'poule/predictions.html'
    ordering = ['-date']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date_list = []
        complete_date_list = list(
            self.get_object().games.annotate(date_formatted=TruncDay('date')).values('date_formatted'))
        complete_game_list = list(self.get_object().games.annotate(date_formatted=TruncDay('date')))
        for date in complete_date_list:
            if date['date_formatted'] not in date_list:
                date_list.append(date['date_formatted'])
        date_dict = {el: [] for el in date_list}
        for game in complete_game_list:
            date_dict[game.date_formatted].append(game)
        context['date_dict'] = date_dict
        return context


class PouleRulesView(DetailView):
    model = Poule
    template_name = 'poule/rules.html'


class PouleGamesView(FormMixin, DetailView):
    model = Poule
    template_name = 'poule/games.html'
    form_class = CreateGameForm

    def get_success_url(self):
        return reverse('poule-games', kwargs={'pk': self.object.pk})

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        object = Poule.objects.get(pk=self.kwargs['pk'])
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            form.instance.poule = object
            form.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class TeamUpdateView(UpdateView):
    model = Team
    template_name = 'poule/teams_update.html'
    fields = ['name', 'image']


class TeamDeleteView(DeleteView):
    model = Team
    template_name = 'poule/teams_delete.html'

    def test_func(self):
        poule = self.get_object()
        if self.request.user == poule.admin:
            return True
        return False


class GameUpdateView(UpdateView):
    model = Game
    template_name = 'poule/games_update.html'
    fields = ['team1', 'team2', 'date', 'result1', 'result2']


class GameDeleteView(DeleteView):
    model = Game
    template_name = 'poule/games_delete.html'

    def test_func(self):
        poule = self.get_object()
        if self.request.user == poule.admin:
            return True
        return False


class PouleTeamsView(FormMixin, DetailView):
    model = Poule
    template_name = 'poule/teams.html'
    form_class = CreateTeamForm

    def get_success_url(self):
        return reverse('poule-teams', kwargs={'pk': self.object.pk})

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        object = Poule.objects.get(pk=self.kwargs['pk'])
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            form.instance.poule = object
            form.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class PouleInfoView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Poule
    template_name = 'lobby/poule_info.html'
    fields = ['name', 'description', 'image', 'sport']

    def form_valid(self, form):
        form.instance.admin = self.request.user
        return super().form_valid(form)

    def test_func(self):
        poule = self.get_object()
        if self.request.user == poule.admin:
            return True
        return False


class PouleDeleteView(DeleteView):
    model = Poule
    success_url = '/'

    def test_func(self):
        poule = self.get_object()
        if self.request.user == poule.admin:
            return True
        return False


def overview(request):
    return render(request, 'poule/overview.html', {'sbar': 'overview'})


def ranking(request):
    return render(request, 'poule/ranking.html', {'sbar': 'ranking'})


def predictions(request):
    return render(request, 'poule/predictions.html', {'sbar': 'predictions'})


def games(request):
    return render(request, 'poule/games.html', {'sbar': 'games'})


def rules(request):
    return render(request, 'poule/rules.html', {'sbar': 'rules'})


def teams(request):
    return render(request, 'poule/teams.html', {'sbar': 'teams'})


def info(request):
    return render(request, 'poule/info.html', {'sbar': 'info'})
