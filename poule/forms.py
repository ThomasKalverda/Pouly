from django import forms
from .models import Team, Game, Prediction, Poule, User

PREDICTION_CHOICES = [
    ('', ''),
    (0, 0),
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, '5+'),
]

GAME_DAYS = [
    (0, 'Monday'),
    (1, 'Tuesday'),
    (2, 'Wednesday'),
    (3, 'Thursday'),
    (4, 'Friday'),
    (5, 'Saturday'),
    (6, 'Sunday'),
]

GAME_TIMES = [
    ('00', '00:00'),
    ('01', '01:00'),
    ('02', '02:00'),
    ('03', '03:00'),
    ('04', '04:00'),
    ('05', '05:00'),
    ('06', '06:00'),
    ('07', '07:00'),
    ('08', '08:00'),
    ('09', '09:00'),
    ('10', '10:00'),
    ('11', '11:00'),
    ('12', '12:00'),
    ('13', '13:00'),
    ('14', '14:00'),
    ('15', '15:00'),
    ('16', '16:00'),
    ('17', '17:00'),
    ('18', '18:00'),
    ('19', '19:00'),
    ('20', '20:00'),
    ('21', '21:00'),
    ('22', '22:00'),
    ('23', '23:00'),
]

TRUE_FALSE_CHOICES = [
    (True, 'Yes'),
    (False, 'No')
]


# Form for PouleInfoView to update the Poule model. Filter admin choices to only contain users of that Poule.
class PouleUpdateForm(forms.ModelForm):
    def __init__(self, poule, *args, **kwargs):
        super(PouleUpdateForm, self).__init__(*args, **kwargs)
        self.fields['admin'].queryset = User.objects.filter(poule=poule)

    class Meta:
        model = Poule
        fields = ['name', 'description', 'admin', 'image', 'sport']


# Form for PouleTeamsView to create Team objects.
class CreateTeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'image']


# Form for PouleGamesView to create Game objects. Filter team choices to only contain teams of that Poule.
class CreateGameForm(forms.ModelForm):
    def __init__(self, poule, *args, **kwargs):
        super(CreateGameForm, self).__init__(*args, **kwargs)
        self.fields['team1'].queryset = Team.objects.filter(poule=poule)
        self.fields['team2'].queryset = Team.objects.filter(poule=poule)

    class Meta:
        model = Game
        fields = ['team1', 'team2', 'date']


# Form for GameUpdateView to update Game objects. Filter team choices to only contain teams of that Poule.
class GameUpdateForm(forms.ModelForm):
    def __init__(self, poule, *args, **kwargs):
        super(GameUpdateForm, self).__init__(*args, **kwargs)
        self.fields['team1'].queryset = Team.objects.filter(poule=poule)
        self.fields['team2'].queryset = Team.objects.filter(poule=poule)

    class Meta:
        model = Game
        fields = ['team1', 'team2', 'date', 'result1', 'result2']


# Form for PoulePredictionView to create Prediction objects. Filter prediction choices to get 0-5+.
# Set style through widget to style from Matrix Admin
class CreatePredictionForm(forms.ModelForm):
    prediction1 = forms.ChoiceField(choices=PREDICTION_CHOICES, widget=forms.Select(
        attrs={'class': 'select form-control custom-select font-weight-bold font-20',
               'style': 'width: 60px; height: 50px;'}))
    prediction2 = forms.ChoiceField(choices=PREDICTION_CHOICES, widget=forms.Select(
        attrs={'class': 'select form-control custom-select font-weight-bold font-20',
               'style': 'width: 60px; height: 50px;'}))

    class Meta:
        model = Prediction
        fields = ['prediction1', 'prediction2']


# Form for PouleCompetitionView to get the settings for creating Game objects.
class CompetitionMakerForm(forms.Form):
    teams = forms.ModelMultipleChoiceField(queryset=Team.objects.all(), widget=forms.Select(
        attrs={'class': "select2 form-control m-t-15",
               'multiple': "multiple",
               'style': "height: 36px;width: 100%;"}))
    home_and_away = forms.ChoiceField(choices=TRUE_FALSE_CHOICES, widget=forms.Select(
        attrs={'class': "form-control m-t-15",
               'style': "height: 36px; width: 100%; border-color: #aaa; border-radius:4px;"}))
    start_date = forms.DateTimeField(widget=forms.widgets.TextInput(
        attrs={'type': 'text',
               'data-date-format': 'dd/mm/yyyy',
               'class': 'datepicker form-control',
               'placeholder': 'dd/mm/yyyy',
               'id': 'datepicker-autoclose',
               'style': 'border-color: #aaa; border-radius:4px;'}))
    game_days = forms.MultipleChoiceField(choices=GAME_DAYS, widget=forms.Select(
        attrs={'class': "select2 form-control m-t-15",
               'multiple': "multiple",
               'style': "height: 36px; width: 100%; border-color: #aaa; border-radius:4px;"}))
    games_per_day = forms.IntegerField(
        widget=forms.NumberInput(attrs={'style': "height: 36px; width: 100%; border-color: #aaa; border-radius:4px;"}))
    game_times = forms.MultipleChoiceField(choices=GAME_TIMES, widget=forms.Select(
        attrs={'class': "select2 form-control m-t-15",
               'multiple': "multiple",
               'style': "height: 36px; width: 100%; border-color: #aaa; border-radius:4px;"}))

    # Filter team choices to only contain teams from that Poule.
    def __init__(self, poule, *args, **kwargs):
        super(CompetitionMakerForm, self).__init__(*args, **kwargs)
        self.fields['teams'].queryset = Team.objects.filter(poule=poule).order_by('name')
