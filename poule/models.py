from django.db import models
from django.contrib.auth.models import User
from lobby.models import Poule
from django.utils import timezone
from django.urls import reverse


class Team(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(default='team_pics/default.jpg', upload_to='team_pics')
    poule = models.ForeignKey(Poule, on_delete=models.CASCADE, related_name='teams')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('poule-teams', kwargs={'pk': self.poule.id})


class Game(models.Model):
    poule = models.ForeignKey(Poule, on_delete=models.CASCADE, related_name='games')
    team1 = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, related_name='games1')
    team2 = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, related_name='games2')
    result1 = models.SmallIntegerField(null=True, blank=True)
    result2 = models.SmallIntegerField(null=True, blank=True)
    date = models.DateTimeField(auto_now=False, auto_now_add=False, default=timezone.now)

    def __str__(self):
        return f'{self.poule}: {self.team1} vs {self.team2} '

    def get_absolute_url(self):
        return reverse('poule-games', kwargs={'pk': self.poule.id})


class Prediction(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='predictions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='predictions')
    prediction1 = models.SmallIntegerField(null=True, blank=True)
    prediction2 = models.SmallIntegerField(null=True, blank=True)
    points = models.SmallIntegerField(null=True, blank=True)

    def __str__(self):
        return f'{self.game}: {self.prediction1} vs {self.prediction2}'


class Score(models.Model):
    points = models.SmallIntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='points')
    poule = models.ForeignKey(Poule, on_delete=models.CASCADE, related_name='points')

    def __str__(self):
        return f'{self.poule}: {self.user} - {self.points}'
