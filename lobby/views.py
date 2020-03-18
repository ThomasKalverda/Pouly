from django.shortcuts import render
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
        'books': books
    }
    return render(request, 'lobby/home.html', context)
