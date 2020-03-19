from django.db import models
from django.contrib.auth.models import User


class Sport(models.Model):
    name = models.CharField(max_length=100, default='Voetbal')
    imageURL = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=100)
    imageURL = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name


class Poule(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=300, blank=True)
    imageURL = models.CharField(max_length=100, blank=True)
    sport = models.ForeignKey(Sport, on_delete=models.SET_NULL, null=True)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin')
    users = models.ManyToManyField(User)
    teams = models.ManyToManyField(Team)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name
