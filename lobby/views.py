from django.shortcuts import render
from .models import Poule
from django.http import HttpResponse

books = [
    {'book1': 'book1',
     'book2': 'book2',
     'book3': 'book3',
     },
    {'book1': 'book1',
     'book2': 'book2',
     'book3': 'book3',
     },
    {'book1': 'book1',
     'book2': 'book2',
     'book3': 'book3',
     },
    {'book1': 'book1',
     'book2': 'book2',
     'book3': 'book3',
     },
    {'book1': 'book1',
     'book2': 'book2',
     'book3': 'book3',
     },
    {'book1': 'book1',
     'book2': 'book2',
     'book3': 'book3',
     },
    {'book1': 'book1',
     'book2': 'book2',
     'book3': 'book3',
     },
    {'book1': 'book1',
     'book2': 'book2',
     'book3': 'book3',
     },
    {'book1': 'book1',
     'book2': 'book2',
     'book3': 'book3',
     },
    {'book1': 'book1',
     'book2': 'book2',
     'book3': 'book3',
     },
    {'book1': 'book1',
     'book2': 'book2',
     'book3': 'book3',
     },

]


def home(request):
    context = {
        'poules': Poule.objects.all()
    }
    return render(request, 'lobby/home.html', context)
