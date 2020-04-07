from django.contrib.staticfiles.storage import staticfiles_storage
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, DeleteView, UpdateView, View
from django.views.generic.detail import SingleObjectMixin
import operator
from lobby.models import Poule
from .models import Game, Team, Prediction, Score
from collections import defaultdict, deque
import random
from django.db.models.functions import TruncDay
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.edit import FormMixin, FormView
from .forms import CreateTeamForm, CreateGameForm, CreatePredictionForm, CompetitionMakerForm, PouleUpdateForm, GameUpdateForm
from collections import OrderedDict
from django.template.defaulttags import register
import datetime, math
from distutils.util import strtobool
from PIL import Image
from django.templatetags.static import static
from django.conf import settings
import pathlib
from django.contrib import messages
from django.utils import timezone
import pickle


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
    if game.result1 > -1 and game.result2 > -1:
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


def generate_games_CO(form, poule, request):
    team_list = list(form['teams'])
    if len(team_list) % 2:  # if odd number of teams, add dummy team to generate matches correctly
        dummy = Team(name='dummy')
        team_list.append(dummy)
    n = len(team_list)
    matches = []
    return_matches = []
    for round in range(1, n):
        for i in range(int(n / 2)):
            matches.append((team_list[i], team_list[n - 1 - i]))
            return_matches.append((team_list[n - 1 - i], team_list[i]))
        team_list.insert(1, team_list.pop())

    if strtobool(form['home_and_away']):
        for match in return_matches:
            matches.append(match)

    if len(list(form['teams'])) % 2:
        matches = [match for match in matches if
                   not match[0] == dummy and not match[1] == dummy]  # Remove all matches with team dummy

    number_of_game_days = math.ceil(len(matches) / form['games_per_day'])
    date_list = []
    date = form['start_date']
    while len(date_list) < number_of_game_days:
        if str(date.weekday()) in form['game_days']:
            date_list.append(date)
        date = date + datetime.timedelta(days=1)
        if len(date_list) == number_of_game_days:
            break

    game_times = list(map(int, form['game_times']))
    game_times_deq = deque(game_times)

    for date in date_list:
        for i in range(form['games_per_day']):
            if len(matches) > 0:
                team1 = matches[0][0]
                team2 = matches[0][1]
                matches.pop(0)
                gamedate = date + datetime.timedelta(hours=game_times_deq[0])
                game = Game(team1=team1, team2=team2, date=gamedate, poule=poule)
                game.save()
                messages.success(request,
                                 f"Game {game.team1} vs {game.team2} on {game.date.strftime('%A %B %d')} at {game.date.strftime('%H:%M')}  added!")
                print(f'Game created: {game}')
            game_times_deq.rotate(-1)


def generate_games_KO(form, poule):
    matches = []
    team_list = form['teams']
    for team in team_list:
        for i in range(len(team_list)):
            if not team == team_list[i]:
                matches.append((team, team_list[i]))

    print(matches)


def generate_teams(number, poule):
    with open('random_teams.pickle', 'rb') as f:
        # The protocol version used is detected automatically, so we do not
        # have to specify it.
        random_teams = pickle.load(f)

        poule_team_names = [team.name for team in Team.objects.filter(poule=poule)]
        length = len(random_teams)
        # check how many teams from the pickle already exist in poule_team_names
        max_number = 64
        for random_team in random_teams:
            if random_team.name in poule_team_names:
                max_number -= 1

        for i in range(min(number,max_number)):
            index = random.randint(0, len(random_teams)-1)
            team = random_teams[index]

            while team.name in poule_team_names:
                if index == 63:
                    index = 0
                else:
                    index += 1
                team = random_teams[index]
            poule_team_names.append(team.name)
            team.poule = poule
            print(team)
            team.save()


def generate_predictions(poule, user):
    user_predictions = user.predictions.all()
    predicted_games = [prediction.game for prediction in user_predictions]
    for game in Game.objects.filter(poule=poule):
        if not game in predicted_games:
            prediction1 = random.randint(0, 5)
            prediction2 = random.randint(0, 5)
            new_prediction = Prediction(user=user, game=game, prediction1=prediction1, prediction2=prediction2)
            new_prediction.save()



def clear_predictions(poule, user):
    user_predictions = user.predictions.all()
    for prediction in user_predictions:
        if prediction.game.date > timezone.now() and prediction.game.poule == poule:
            prediction.delete()


class PouleOverviewView(UserPassesTestMixin, DetailView):
    model = Poule
    template_name = 'poule/overview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        upcoming_games = Game.objects.filter(poule=self.get_object(), date__gte=timezone.now()).order_by('date')[:3]
        played_games = Game.objects.filter(result1__gte=0, result2__gte=0, poule=self.get_object(),
                                           date__lte=timezone.now()).order_by('-date')
        user_predictions = self.request.user.predictions.all()
        context['prediction_dict'] = {prediction.game: prediction for prediction in user_predictions}
        context['upcoming_games'] = upcoming_games
        context['played_games'] = played_games
        return context

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
        for key, value in games_grouped_by_date.items():
            value.sort(key=lambda r: r.date)
        context['grouped_and_sorted_games'] = sorted(games_grouped_by_date.items())
        user_predictions = self.request.user.predictions.all()
        context['prediction_dict'] = {prediction.game: prediction for prediction in user_predictions}
        point_dict = {10: 0, 6: 0, 4: 0, 'total': 0}
        for prediction in user_predictions:
            if prediction.points and prediction.game.poule == self.get_object():
                point_dict[prediction.points] += prediction.points
                point_dict['total'] += prediction.points

        context['point_dict'] = point_dict
        context['now'] = timezone.now()
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        if request.POST.get('gameid'):
            game = Game.objects.get(pk=request.POST.get('gameid'))
        form = self.get_form()
        if 'save' in request.POST:
            if form.is_valid():
                old_prediction = Prediction.objects.filter(user=self.request.user, game=game)
                if old_prediction:
                    old_prediction.delete()
                form.instance.game = game
                form.instance.user = self.request.user
                form.save()
                messages.success(request,
                                 f"Prediction {form.instance.game.team1} {form.cleaned_data.get('prediction1')} - {form.cleaned_data.get('prediction2')} {form.instance.game.team2} saved!")
                return HttpResponseRedirect(self.get_success_url(**kwargs))
            else:
                return self.form_invalid(form)
        elif 'randomize' in request.POST:
            generate_predictions(self.get_object(), request.user)
            return self.form_valid(form)
        elif 'clear' in request.POST:
            clear_predictions(self.get_object(), request.user)
            return self.form_valid(form)

    def get_success_url(self, **kwargs):
        if kwargs:
            return reverse_lazy('poule-predictions', kwargs={'pk': kwargs['pk']})
        else:
            return reverse_lazy('poule-predictions', args=(self.get_object().id,))



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
            date = form.cleaned_data.get('date')
            form.save()
            messages.success(request,
                             f"Game {form.cleaned_data.get('team1')} vs {form.cleaned_data.get('team2')} on {date.strftime('%A %B %d')} at {date.strftime('%H:%M')}  added!")

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        poule = self.object.poule
        context['poule'] = poule
        return context


class TeamDeleteView(DeleteView):
    model = Team
    template_name = 'poule/teams_delete.html'

    def test_func(self):
        poule = self.get_object()
        if self.request.user == poule.admin:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        poule = self.object.poule
        context['poule'] = poule
        return context

    #
    def get_success_url(self):
        return reverse('poule-teams', kwargs={'pk': self.object.poule.pk})


class GameUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Game
    template_name = 'poule/games_update.html'
    form_class = GameUpdateForm

    def test_func(self):
        poule = self.get_object().poule
        if self.request.user == poule.admin:
            return True
        return False

    def form_valid(self, form):
        poule = form.instance.poule
        game = form.instance
        if form.is_valid():
            form.save()
            calculate_prediction_points(poule, game)
            calculate_scores(poule)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('poule-games', kwargs={'pk': self.object.poule.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        poule = self.object.poule
        context['poule'] = poule
        return context

    def get_form_kwargs(self):
        kwargs = super(GameUpdateView, self).get_form_kwargs()
        # Update the existing form kwargs dict with the poule.
        kwargs.update({"poule": self.object.poule})
        return kwargs


class GameDeleteView(UserPassesTestMixin, DeleteView):
    model = Game
    template_name = 'poule/games_delete.html'

    def test_func(self):
        poule = self.get_object().poule
        if self.request.user == poule.admin:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        poule = self.object.poule
        context['poule'] = poule
        return context

    def get_success_url(self):
        return reverse('poule-games', kwargs={'pk': self.object.poule.pk})


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
        if 'add' in request.POST:
            if form.is_valid():
                form.instance.poule = object
                form.save()
                messages.success(request,
                                 f"Team {form.cleaned_data.get('name')} added!")
                return self.form_valid(form)
            else:
                return self.form_invalid(form)
        elif 'generate' in request.POST:
            number = int(form.data['number'])
            generate_teams(number, object)
            return self.form_valid(form)


class PouleCompetitionView(FormMixin, DetailView):
    model = Poule
    template_name = 'poule/competition.html'
    form_class = CompetitionMakerForm
    success_url = reverse_lazy('poule-games')

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        object = Poule.objects.get(pk=self.kwargs['pk'])
        self.object = self.get_object()
        form = self.get_form()
        team_list = request.POST.getlist('teams')
        day_list = request.POST.getlist('game_days')
        time_list = request.POST.getlist('game_times')
        start_date = form.data['start_date']
        date = datetime.datetime.strptime(start_date, '%d/%m/%Y')
        form.data = form.data.copy()
        form.data['teams'] = team_list
        form.data['game_days'] = day_list
        form.data['start_date'] = date
        form.data['game_times'] = time_list
        if form.is_valid():
            generate_games_CO(form.cleaned_data, object, request)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super(PouleCompetitionView, self).get_form_kwargs()
        # Update the existing form kwargs dict with the poule.
        kwargs.update({"poule": self.object})
        return kwargs

    def get_success_url(self, **kwargs):
        if kwargs:
            return reverse_lazy('poule-games', kwargs={'pk': kwargs['pk']})
        else:
            return reverse_lazy('poule-games', args=(self.object.id,))


class PouleInfoView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Poule
    template_name = 'lobby/poule_info.html'
    form_class = PouleUpdateForm

    def test_func(self):
        poule = self.get_object()
        if self.request.user == poule.admin:
            return True
        return False

    def get_form_kwargs(self):
        kwargs = super(PouleInfoView, self).get_form_kwargs()
        # Update the existing form kwargs dict with the poule.
        kwargs.update({"poule": self.object})
        return kwargs


class PouleDeleteView(DeleteView):
    model = Poule
    success_url = '/'

    def test_func(self):
        poule = self.get_object()
        if self.request.user == poule.admin:
            return True
        return False
