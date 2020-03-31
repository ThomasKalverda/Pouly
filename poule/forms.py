from django import forms
from .models import Team, Game, Prediction

PREDICTION_CHOICES = [
    ('', ''),
    (0, 0),
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, '5+'),
]


class CreateTeamForm(forms.ModelForm):
     class Meta:
        model = Team
        fields = ['name', 'image']


class CreateGameForm(forms.ModelForm):
    def __init__(self, poule, *args, **kwargs):
        super(CreateGameForm, self).__init__(*args, **kwargs)  # populates the post
        self.fields['team1'].queryset = Team.objects.filter(poule=poule)
        self.fields['team2'].queryset = Team.objects.filter(poule=poule)

    class Meta:
        model = Game
        fields = ['team1', 'team2', 'date']


class CreatePredictionForm(forms.ModelForm):
    prediction1 = forms.ChoiceField(choices=PREDICTION_CHOICES, widget=forms.Select(attrs={'class': 'select form-control custom-select font-weight-bold font-20', 'style': 'width: 60px; height: 50px;'}))
    prediction2 = forms.ChoiceField(choices=PREDICTION_CHOICES, widget=forms.Select(attrs={'class': 'select form-control custom-select font-weight-bold font-20', 'style': 'width: 60px; height: 50px;'}))

    class Meta:
        model = Prediction
        fields = ['prediction1', 'prediction2']
