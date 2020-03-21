from django.shortcuts import render
from django.views.generic import ListView, DetailView, DeleteView
from lobby.models import Poule
from .models import Game
from django.db.models.functions import TruncDay


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date_list = []
        complete_date_list = list(
            self.get_object().games.annotate(date_formatted=TruncDay('date')).values('date_formatted'))
        complete_game_list = list(self.get_object().games.annotate(date_formatted=TruncDay('date')))
        for date in complete_date_list:
            if date['date_formatted'] not in date_list:
                date_list.append(date['date_formatted'])
        date_dict = {el:[] for el in date_list}
        for game in complete_game_list:
            date_dict[game.date_formatted].append(game)
        context['date_list'] = date_list
        context['date_dict'] = date_dict
        return context


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
