from django import forms
from .models import Team, Game


class CreateTeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'image']


class CreateGameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['team1', 'team2', 'date']
