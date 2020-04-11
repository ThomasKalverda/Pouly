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
from .forms import CreateTeamForm, CreateGameForm, CreatePredictionForm, CompetitionMakerForm, PouleUpdateForm, \
    GameUpdateForm
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


# Filter for templates to get values by key for dicts
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


# Method to calculate all scores for users in the Poule.
def calculate_scores(poule):
    # Iterate over users
    for user in poule.users.all():
        new_points = 0

        # Get all predictions of the user for this poule.
        user_predictions = Prediction.objects.filter(user=user, game__poule=poule)

        # Add prediction points to new_points if the prediction has points for each prediction in user_predictions
        for prediction in user_predictions:
            if prediction.points:
                new_points += prediction.points

        # Save the new_points to the score of the user
        score = Score.objects.get(user=user, poule=poule)
        score.points = new_points
        score.save()


# Method to calculate all predictions points belonging to a certain game.
def calculate_prediction_points(poule, game):
    # Get all predictions belonging to the game.
    game_predictions = Prediction.objects.all().filter(game=game)

    # Iterate over the predictions if the game has a valid result
    if game.result1 is not None and game.result2 is not None:
        if game.result1 > -1 and game.result2 > -1:

            for prediction in game_predictions:

                # Calculate result differences
                diff1 = game.result1 - prediction.prediction1
                diff2 = game.result2 - prediction.prediction2

                # Determine winner
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

                # Determine number of points
                if diff1 == 0 and diff2 == 0:
                    prediction.points = 10
                elif diff1 == diff2:
                    prediction.points = 6
                elif res_winner == pred_winner:
                    prediction.points = 4
                else:
                    prediction.points = 0
                prediction.save()


# Method to generate games for the Competition Maker.
def generate_games_CO(form, poule, request):
    # Get list of teams from the form.
    team_list = list(form['teams'])

    # if odd number of teams, add dummy team to generate matches correctly
    if len(team_list) % 2:
        dummy = Team(name='dummy')
        team_list.append(dummy)

    # initialize length and match lists
    n = len(team_list)
    matches = []
    return_matches = []

    # Iterate over the length-1, because there should be that many rounds
    for round in range(1, n):

        # Iterate over length/2, because there should be that many matches in a round
        for i in range(int(n / 2)):

            # Make tuples of matches and return matches
            matches.append((team_list[i], team_list[n - 1 - i]))
            return_matches.append((team_list[n - 1 - i], team_list[i]))

        # Rotate team list so teams play against other teams in the next round
        team_list.insert(1, team_list.pop())

    # If there should be return matches, append those to the matches list
    if strtobool(form['home_and_away']):
        for match in return_matches:
            matches.append(match)

    # Remove all matches with the dummy team.
    if len(list(form['teams'])) % 2:
        matches = [match for match in matches if
                   not match[0] == dummy and not match[1] == dummy]

    # Initialize date list and start date
    number_of_game_days = math.ceil(len(matches) / form['games_per_day'])
    date_list = []
    date = form['start_date']

    # Add date to date_list if the weekday is correct, as long as the date_list is not long enough
    while len(date_list) < number_of_game_days:
        if str(date.weekday()) in form['game_days']:
            date_list.append(date)
        date = date + datetime.timedelta(days=1)

        # If date_list is long enough, break from while
        if len(date_list) == number_of_game_days:
            break

    # Get number of matches for user message
    number_of_matches = len(matches)

    # Initialize game times deq from form
    game_times = list(map(int, form['game_times']))
    game_times_deq = deque(game_times)

    # Iterate over the dates and make Game objects from matches. Get time from the game times deque
    for date in date_list:
        for i in range(form['games_per_day']):
            if len(matches) > 0:
                # Get teams from match tuple
                team1 = matches[0][0]
                team2 = matches[0][1]
                matches.pop(0)

                # Get datetime from current date and game time deq
                gamedate = date + datetime.timedelta(hours=game_times_deq[0])
                game = Game(team1=team1, team2=team2, date=gamedate, poule=poule)
                game.save()
                print(f'Game created: {game}')
            # Rotate deque to get the next game time
            game_times_deq.rotate(-1)
    messages.success(request, f"{number_of_matches} games added!")


# Method to generate teams for TeamsView
def generate_teams(number, poule):
    # Open the pickle with 64 country Team objects
    with open('random_teams.pickle', 'rb') as f:
        random_teams = pickle.load(f)

        # Get all team names that are currently in the poule
        poule_team_names = [team.name for team in Team.objects.filter(poule=poule)]
        length = len(random_teams)

        # Check how many teams from the pickle already exist in poule_team_names and substract from max
        max_number = 64
        for random_team in random_teams:
            if random_team.name in poule_team_names:
                max_number -= 1

        # For the number of teams to be added, get a random Team from the pickle and save it to the Poule
        for i in range(min(number, max_number)):
            index = random.randint(0, len(random_teams) - 1)
            team = random_teams[index]

            # Check if team name is already in the poule, if so, get other index and check again
            while team.name in poule_team_names:
                if index == 63:
                    index = 0
                else:
                    index += 1
                team = random_teams[index]

            # Add name to list, so teams are not added more than once
            poule_team_names.append(team.name)

            # Save team to the poule
            team.poule = poule
            print(team)
            team.save()


# Method to randomly make predictions for the user.
def generate_predictions(poule, user):
    # Get all already predicted games
    user_predictions = user.predictions.all()
    predicted_games = [prediction.game for prediction in user_predictions if prediction.game.date > timezone.now()]

    # Iterate over the games in the poule and if no prediction has been made, game hasn't been played and
    # game date is in the future, create prediction with random values.
    for game in Game.objects.filter(poule=poule):
        if not game in predicted_games and not game.result1 and not game.result2 and game.date > timezone.now():
            prediction1 = random.randint(0, 5)
            prediction2 = random.randint(0, 5)
            new_prediction = Prediction(user=user, game=game, prediction1=prediction1, prediction2=prediction2)
            new_prediction.save()


# Method to delete all predictions for future games.
def clear_predictions(poule, user):
    # Get all predictions from the user
    user_predictions = user.predictions.all()

    # Delete prediction if game date is in the future, the poule is the current one and the game has no results yet.
    for prediction in user_predictions:
        if prediction.game.date > timezone.now() and prediction.game.poule == poule and not prediction.game.result1 and not prediction.game.result2:
            prediction.delete()


# CBV for overview page of Poule. Only accessable if user is logged in.
class PouleOverviewView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Poule
    template_name = 'poule/overview.html'

    # Set extra context data for the template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get three future games with no result yet, ordered by date.
        upcoming_games = Game.objects.filter(
            result1=None,
            result2=None,
            poule=self.get_object(),
            date__gte=timezone.now()).order_by('date')[:3]
        context['upcoming_games'] = upcoming_games

        # Get all games with results greater than or equal to 0, ordered by desc date.
        played_games = Game.objects.filter(result1__gte=0, result2__gte=0, poule=self.get_object()).order_by('-date')
        context['played_games'] = played_games

        # Get all user predictions in a dict with the game as the key
        user_predictions = self.request.user.predictions.all()
        context['prediction_dict'] = {prediction.game: prediction for prediction in user_predictions}

        return context

    # Check if user is in the poule, if not, add user to the poule and create a new Score for the user.
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


# CBV for ranking page of the poule. Only accessable if user is logged in.
class PouleRankingView(LoginRequiredMixin, DetailView):
    model = Poule
    template_name = 'poule/ranking.html'

    # Set extra context data for the template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get scores dict with users as keys and sorted scores as values
        users = self.get_object().users.all()
        scores = {}
        for user in users:
            scores[user] = Score.objects.filter(user=user, poule=self.get_object()).first().points
        sorted_d = dict(sorted(scores.items(), key=operator.itemgetter(1), reverse=True))
        context['scores'] = sorted_d
        return context


# CBV for prediction page of the poule. Only accessable to logged in users
class PoulePredictionsView(LoginRequiredMixin, FormMixin, DetailView):
    model = Poule
    template_name = 'poule/predictions.html'
    form_class = CreatePredictionForm
    success_url = reverse_lazy('poule-predictions')

    # Set extra context data to the template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get a sorted dict with dates as keys and game lists as values
        games_grouped_by_date = defaultdict(list)
        for game in self.get_object().games.all():
            games_grouped_by_date[game.date.date()].append(game)
        for key, value in games_grouped_by_date.items():
            value.sort(key=lambda r: r.date)
        context['grouped_and_sorted_games'] = sorted(games_grouped_by_date.items())

        # Get all user predictions in a dict with the game as the key
        user_predictions = self.request.user.predictions.all()
        context['prediction_dict'] = {prediction.game: prediction for prediction in user_predictions}

        # Get a dict with points as keys and total user predictions points per key as values
        point_dict = {10: 0, 6: 0, 4: 0, 'total': 0}
        for prediction in user_predictions:
            if prediction.points and prediction.game.poule == self.get_object():
                point_dict[prediction.points] += prediction.points
                point_dict['total'] += prediction.points
        context['point_dict'] = point_dict

        # Get the current datetime
        context['now'] = timezone.now()
        return context

    # Override post method to validate form and save predictions
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        if request.POST.get('gameid'):
            game = Game.objects.get(pk=request.POST.get('gameid'))
        form = self.get_form()

        # Check which button was clicked
        if 'save' in request.POST:
            if form.is_valid():

                # Delete old predictions for that game and current user
                old_prediction = Prediction.objects.filter(user=self.request.user, game=game)
                if old_prediction:
                    old_prediction.delete()

                # Save form creating a new prediction for the game and current user
                form.instance.game = game
                form.instance.user = self.request.user
                form.save()

                # Show success message
                messages.success(request,
                                 f"Prediction {form.instance.game.team1} {form.cleaned_data.get('prediction1')} - {form.cleaned_data.get('prediction2')} {form.instance.game.team2} saved!")
                return HttpResponseRedirect(self.get_success_url(**kwargs))
            else:
                return self.form_invalid(form)
        elif 'randomize' in request.POST:
            # Run method generate_predictions
            generate_predictions(self.get_object(), request.user)
            return self.form_valid(form)
        elif 'clear' in request.POST:
            # Run method clear_predictions
            clear_predictions(self.get_object(), request.user)
            return self.form_valid(form)

    def get_success_url(self, **kwargs):
        if kwargs:
            return reverse_lazy('poule-predictions', kwargs={'pk': kwargs['pk']})
        else:
            return reverse_lazy('poule-predictions', args=(self.get_object().id,))


# CBV for games page of the poule. Only accessable for logged in admin.
class PouleGamesView(LoginRequiredMixin, UserPassesTestMixin, FormMixin, DetailView):
    model = Poule
    template_name = 'poule/games.html'
    form_class = CreateGameForm

    # Check if logged in user is poule admin
    def test_func(self):
        poule = self.get_object()
        if self.request.user == poule.admin:
            return True
        return False

    def get_success_url(self):
        return reverse('poule-games', kwargs={'pk': self.object.pk})

    # Override post method to save form
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        object = Poule.objects.get(pk=self.kwargs['pk'])
        self.object = self.get_object()
        form = self.get_form()

        # Check if form is valid and if so, save form creating a new Game
        if form.is_valid():
            form.instance.poule = object
            date = form.cleaned_data.get('date')
            form.save()
            messages.success(request,
                             f"Game {form.cleaned_data.get('team1')} vs {form.cleaned_data.get('team2')} on {date.strftime('%A %B %d')} at {date.strftime('%H:%M')}  added!")

            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    # Set extra form kwargs, so teams field can be filtered on current poule
    def get_form_kwargs(self):
        kwargs = super(PouleGamesView, self).get_form_kwargs()
        # Update the existing form kwargs dict with the poule.
        kwargs.update({"poule": self.object})
        return kwargs


# CBV for updating game objects. Only accessable for logged in admin
class GameUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Game
    template_name = 'poule/games_update.html'
    form_class = GameUpdateForm

    # Check if logged in user is poule admin
    def test_func(self):
        poule = self.get_object().poule
        if self.request.user == poule.admin:
            return True
        return False

    # Check if form is valid, if so, save form updating the game, then run two methods to calculate prediction
    # points and poule scores
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

    # Set extra context data so sidebar navigation works correctly
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        poule = self.object.poule
        context['poule'] = poule
        return context

    # Set extra form kwargs, so teams field can be filtered on current poule
    def get_form_kwargs(self):
        kwargs = super(GameUpdateView, self).get_form_kwargs()
        # Update the existing form kwargs dict with the poule.
        kwargs.update({"poule": self.object.poule})
        return kwargs


# CBV for deleting game objects. Only accessable for logged in admin
class GameDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Game
    template_name = 'poule/games_delete.html'

    # Check if logged in user is poule admin
    def test_func(self):
        poule = self.get_object().poule
        if self.request.user == poule.admin:
            return True
        return False

    # Set extra context data so sidebar navigation works correctly
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        poule = self.object.poule
        context['poule'] = poule
        return context

    def get_success_url(self):
        return reverse('poule-games', kwargs={'pk': self.object.poule.pk})


# CBV for teams page of the poule. Only accessable for logged in admin.
class PouleTeamsView(LoginRequiredMixin, UserPassesTestMixin, FormMixin, DetailView):
    model = Poule
    template_name = 'poule/teams.html'
    form_class = CreateTeamForm

    # Check if logged in user is poule admin
    def test_func(self):
        poule = self.get_object()
        if self.request.user == poule.admin:
            return True
        return False

    def get_success_url(self):
        return reverse('poule-teams', kwargs={'pk': self.object.pk})

    # Override post to save form
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        object = Poule.objects.get(pk=self.kwargs['pk'])
        self.object = self.get_object()
        form = self.get_form()

        # Check which button was clicked
        if 'add' in request.POST:
            # Check if form is valid and if so, save form creating a new Team
            if form.is_valid():
                form.instance.poule = object
                form.save()
                messages.success(request,
                                 f"Team {form.cleaned_data.get('name')} added!")
                return self.form_valid(form)
            else:
                return self.form_invalid(form)
        elif 'generate' in request.POST:
            # Get number from form and run method to generate teams from pickle
            number = int(form.data['number'])
            generate_teams(number, object)
            return self.form_valid(form)


# CBV for updating Team objects. Only accessable for logged in admin
class TeamUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Team
    template_name = 'poule/teams_update.html'
    fields = ['name', 'image']

    # Check if logged in user is poule admin
    def test_func(self):
        poule = self.get_object().poule
        if self.request.user == poule.admin:
            return True
        return False

    # Set extra context data so sidebar navigation works correctly
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        poule = self.object.poule
        context['poule'] = poule
        return context


# CBV for deleting Team objects. Only accessable for logged in admin
class TeamDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Team
    template_name = 'poule/teams_delete.html'

    # Check if logged in user is poule admin
    def test_func(self):
        poule = self.get_object().poule
        if self.request.user == poule.admin:
            return True
        return False

    # Set extra context data so sidebar navigation works correctly
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        poule = self.object.poule
        context['poule'] = poule
        return context

    def get_success_url(self):
        return reverse('poule-teams', kwargs={'pk': self.object.poule.pk})


# CBV for competition maker page. Only accessable for logged in admin
class PouleCompetitionView(LoginRequiredMixin, UserPassesTestMixin, FormMixin, DetailView):
    model = Poule
    template_name = 'poule/competition.html'
    form_class = CompetitionMakerForm
    success_url = reverse_lazy('poule-games')

    # Check if logged in user is poule admin
    def test_func(self):
        poule = self.get_object()
        if self.request.user == poule.admin:
            return True
        return False

    # Override post to get all form data to the generate games method
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        object = Poule.objects.get(pk=self.kwargs['pk'])
        self.object = self.get_object()
        form = self.get_form()

        # Get lists from the POST data
        team_list = request.POST.getlist('teams')
        day_list = request.POST.getlist('game_days')
        time_list = request.POST.getlist('game_times')
        start_date = form.data['start_date']
        date = datetime.datetime.strptime(start_date, '%d/%m/%Y')

        # Set form data to the lists from POST data
        form.data = form.data.copy()
        form.data['teams'] = team_list
        form.data['game_days'] = day_list
        form.data['start_date'] = date
        form.data['game_times'] = time_list
        if form.is_valid():
            # Run method to generate games
            generate_games_CO(form.cleaned_data, object, request)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    # Set extra form kwargs, so teams field can be filtered on current poule
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


# CBV for updating Poule object.
class PouleInfoView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Poule
    template_name = 'lobby/poule_info.html'
    form_class = PouleUpdateForm

    # Check if logged in user is poule admin
    def test_func(self):
        poule = self.get_object()
        if self.request.user == poule.admin:
            return True
        return False

    # Set extra context data so sidebar navigation works correctly
    def get_form_kwargs(self):
        kwargs = super(PouleInfoView, self).get_form_kwargs()
        # Update the existing form kwargs dict with the poule.
        kwargs.update({"poule": self.object})
        return kwargs


class PouleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Poule
    success_url = '/'

    # Check if logged in user is poule admin
    def test_func(self):
        poule = self.get_object()
        if self.request.user == poule.admin:
            return True
        return False
