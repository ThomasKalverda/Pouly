from django import forms
from .models import Team, Game, Prediction

PREDICTION_CHOICES = [
    (0, 0),
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 4),
    (5, 5),
]

class CreateTeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'image']


class CreateGameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['team1', 'team2', 'date']


class CreatePredictionForm(forms.ModelForm):
    prediction1 = forms.ChoiceField(choices=PREDICTION_CHOICES)
    prediction2 = forms.ChoiceField(choices=PREDICTION_CHOICES)

    class Meta:
        model = Prediction
        fields = ['prediction1', 'prediction2']
