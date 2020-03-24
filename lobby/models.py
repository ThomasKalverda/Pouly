from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Sport(models.Model):
    name = models.CharField(max_length=100, default='Voetbal')
    image = models.ImageField(default='sport_pics/default.jpg', upload_to='sport_pics')

    def __str__(self):
        return self.name


class Poule(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=300, blank=True)
    image = models.ImageField(default='poule_pics/default.jpg', upload_to='poule_pics')
    sport = models.ForeignKey(Sport, on_delete=models.SET_NULL, null=True)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin')
    users = models.ManyToManyField(User)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('poule-overview', kwargs={'pk': self.id})
