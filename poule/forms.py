from django import forms
from .models import Team


class CreateTeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name', 'image']
