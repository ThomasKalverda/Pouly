from django.db import models
from django.contrib.auth.models import User
from lobby.models import Poule, Team
from django.utils import timezone


class Game(models.Model):
    poule = models.ForeignKey(Poule, on_delete=models.CASCADE, related_name='games')
    team1 = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, related_name='team1')
    team2 = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, related_name='team2')
    result1 = models.SmallIntegerField(null=True, blank=True)
    result2 = models.SmallIntegerField(null=True, blank=True)
    date = models.DateTimeField(auto_now=False, auto_now_add=False, default=timezone.now)

    def __str__(self):
        return f'{self.poule}: {self.team1} vs {self.team2} '
