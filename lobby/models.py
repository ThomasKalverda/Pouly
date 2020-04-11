from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from PIL import Image


# Model for a sport
class Sport(models.Model):
    name = models.CharField(max_length=100, default='Voetbal')
    image = models.ImageField(default='sport_pics/default.jpg', upload_to='sport_pics')

    def __str__(self):
        return self.name


# Model for a poule
class Poule(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=145, blank=True)
    image = models.ImageField(default='poule_pics/default-poule.jpg', upload_to='poule_pics')
    sport = models.ForeignKey(Sport, on_delete=models.SET_NULL, null=True)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='poules')
    users = models.ManyToManyField(User)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    # Set standard URL for Poule model.
    def get_absolute_url(self):
        return reverse('poule-overview', kwargs={'pk': self.id})

    # Override to make image square and smaller
    def save(self, *args, **kwargs):
        super().save()

        img = Image.open(self.image.path)
        width, height = img.size  # Get dimensions

        if width > 300 and height > 300:
            # keep ratio but shrink down
            img.thumbnail((width, height))

        # check which one is smaller
        if height < width:
            # make square by cutting off equal amounts left and right
            left = (width - height) / 2
            right = (width + height) / 2
            top = 0
            bottom = height
            img = img.crop((left, top, right, bottom))

        elif width < height:
            # make square by cutting off bottom
            left = 0
            right = width
            top = 0
            bottom = width
            img = img.crop((left, top, right, bottom))

        if width > 300 and height > 300:
            img.thumbnail((300, 300))

        img.save(self.image.path)
