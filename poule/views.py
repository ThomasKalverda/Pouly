from django.shortcuts import render
from django.views.generic import ListView, DetailView, DeleteView
from lobby.models import Poule


class PouleOverviewView(DetailView):
    model = Poule
    template_name = 'poule/overview.html'


class PouleRankingView(DetailView):
    model = Poule
    template_name = 'poule/ranking.html'


class PoulePredictionsView(DetailView):
    model = Poule
    template_name = 'poule/predictions.html'


class PouleRulesView(DetailView):
    model = Poule
    template_name = 'poule/rules.html'


class PouleGamesView(DetailView):
    model = Poule
    template_name = 'poule/games.html'


class PouleTeamsView(DetailView):
    model = Poule
    template_name = 'poule/teams.html'


class PouleInfoView(DetailView):
    model = Poule
    template_name = 'poule/info.html'



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