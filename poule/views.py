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

    # def get_form_kwargs(self):
    #     kwargs = super(PoulePredictionsView, self).get_form_kwargs()
    #     query_Prediction = self.request.GET.get('Prediction')
    #     prediction = Prediction.objects.filter(NumeroIdentification=query_Prediction)
    #     kwargs['prediction_qs'] = prediction
    #     u = request.user
    #     kwargs['user_initial'] = '{lname} {fname}'.format(lname=u.last_name, fname=u.first_name)
    #     return kwargs


# class PoulePredictionsView(FormMixin, DetailView):
#     model = Poule
#     template_name = 'poule/predictions.html'
#     ordering = ['-date']
#     form_class = CreatePredictionForm
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         date_list = []
#         complete_date_list = list(
#             self.get_object().games.annotate(date_formatted=TruncDay('date')).values('date_formatted'))
#         complete_game_list = list(self.get_object().games.annotate(date_formatted=TruncDay('date')))
#         for date in complete_date_list:
#             if date['date_formatted'] not in date_list:
#                 date_list.append(date['date_formatted'])
#         date_dict = {el: [] for el in date_list}
#         for game in complete_game_list:
#             date_dict[game.date_formatted].append(game)
#         context['date_dict'] = date_dict
#         return context
#
#     def post(self, request, *args, **kwargs):
#         if not request.user.is_authenticated:
#             return HttpResponseForbidden()
#         object = Poule.objects.get(pk=self.kwargs['pk'])
#         game = Game.objects.get(pk=1)
#         self.object = self.get_object()
#         if request.method == 'POST':
#             form = self.get_form()
#         else:
#             form = self.get_form()
#         if form.is_valid():
#             form.instance.poule = object
#             form.instance.game = game
#             form.instance.user = self.request.user
#             form.save()
#             return self.form_valid(form)
#         else:
#             return self.form_invalid(form)
#
#     def get_success_url(self):
#         return reverse('poule-predictions', kwargs={'pk': self.object.pk})
# # class PouleSavePrediction(FormMixin, DetailView):


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
