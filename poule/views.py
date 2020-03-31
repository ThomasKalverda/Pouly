from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, DeleteView, UpdateView, View
from django.views.generic.detail import SingleObjectMixin
import operator
from lobby.models import Poule
from .models import Game, Team, Prediction, Score
from collections import defaultdict
from django.db.models.functions import TruncDay
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import FormMixin, FormView
from .forms import CreateTeamForm, CreateGameForm, CreatePredictionForm
from collections import OrderedDict
from django.template.defaulttags import register


@register.filter
def get_game_prediction1(dictionary, key):
    return dictionary.get(key).prediction1


@register.filter
def get_game_prediction2(dictionary, key):
    return dictionary.get(key).prediction2


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_game_prediction_points(dictionary, key):
    return dictionary.get(key).points


def calculate_scores(poule):
    poule_games = Game.objects.all().filter(poule=poule)
    poule_predictions = []
    for game in poule_games:
        game_predictions = Prediction.objects.all().filter(game=game)
        for prediction in game_predictions:
            poule_predictions.append(prediction)
    poule_scores = Score.objects.filter(poule=poule)
    for score in poule_scores:
        new_points = 0
        for prediction in poule_predictions:
            if score.user == prediction.user:
                if prediction.points:
                    new_points += prediction.points
        score.points = new_points
        score.save()


def calculate_prediction_points(poule, game):
    game_predictions = Prediction.objects.all().filter(game=game)
    if game.result1 and game.result2:
        for prediction in game_predictions:
            diff1 = game.result1 - prediction.prediction1
            diff2 = game.result2 - prediction.prediction2
            # determine winner
            res_winner = 'team1'
            pred_winner = 'team1'
            if game.result2 > game.result1:
                res_winner = 'team2'
            elif game.result2 == game.result1:
                res_winner = 'tie'
            if prediction.prediction2 > prediction.prediction1:
                pred_winner = 'team2'
            elif prediction.prediction2 == prediction.prediction1:
                pred_winner = 'tie'
            # determine number of points
            if diff1 == 0 and diff2 == 0:
                prediction.points = 10
            elif diff1 == diff2:
                prediction.points = 6
            elif res_winner == pred_winner:
                prediction.points = 4
            else:
                prediction.points = 0
            prediction.save()


class PouleOverviewView(UserPassesTestMixin, DetailView):
    model = Poule
    template_name = 'poule/overview.html'

    def test_func(self):
        poule = self.get_object()
        if self.request.user in poule.users.all():
            return True
        elif self.request.user not in poule.users.all():
            poule.users.add(self.request.user)
            score = Score(poule=poule, user=self.request.user)
            score.save()
            return True
        else:
            return False


class PouleRankingView(DetailView):
    model = Poule
    template_name = 'poule/ranking.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        users = self.get_object().users.all()
        scores = {}
        for user in users:
            scores[user] = Score.objects.filter(user=user, poule=self.get_object()).first().points
        sorted_d = dict(sorted(scores.items(), key=operator.itemgetter(1), reverse=True))
        context['scores'] = sorted_d
        return context


class PoulePredictionsView(FormMixin, DetailView):
    model = Poule
    template_name = 'poule/predictions.html'
    form_class = CreatePredictionForm
    success_url = reverse_lazy('poule-predictions')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        games_grouped_by_date = defaultdict(list)
        for game in self.get_object().games.all():
            games_grouped_by_date[game.date.date()].append(game)
        context['grouped_and_sorted_games'] = sorted(games_grouped_by_date.items())
        user_predictions = self.request.user.predictions.all()
        context['prediction_dict'] = {prediction.game: prediction for prediction in user_predictions}
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        game = Game.objects.get(pk=request.POST.get('gameid'))
        form = self.get_form()

        if form.is_valid():
            old_prediction = Prediction.objects.filter(user=self.request.user, game=game)
            if old_prediction:
                old_prediction.delete()
            form.instance.game = game
            form.instance.user = self.request.user
            form.save()
            return HttpResponseRedirect(self.get_success_url(**kwargs))
        else:
            return self.form_invalid(form)

    def get_success_url(self, **kwargs):
        if kwargs:
            return reverse_lazy('poule-predictions', kwargs={'pk': kwargs['pk']})
        else:
            return reverse_lazy('poule-predictions', args=(self.object.id,))


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

    def get_form_kwargs(self):
        kwargs = super(PouleGamesView, self).get_form_kwargs()
        # Update the existing form kwargs dict with the poule.
        kwargs.update({"poule": self.object})
        return kwargs


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


    def form_valid(self, form):
        poule = form.instance.poule
        game = form.instance
        if form.is_valid():
            form.save()
            calculate_prediction_points(poule, game)
            calculate_scores(poule)
        return super().form_valid(form)


class GameDeleteView(UserPassesTestMixin, DeleteView):
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
    fields = ['name', 'description', 'admin', 'image', 'sport']

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
