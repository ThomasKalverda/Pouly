from django.contrib import admin
from .models import Game, Prediction, Score, Team

admin.site.register(Team)
admin.site.register(Game)
admin.site.register(Prediction)
admin.site.register(Score)
