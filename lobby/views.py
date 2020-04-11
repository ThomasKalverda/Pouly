from django.views.generic import ListView, CreateView
from .models import Poule
from django.contrib.auth.mixins import LoginRequiredMixin


# CBV for the lobby, model is Poule, object in template is 'poules'
class PouleListView(ListView):
    model = Poule
    template_name = 'lobby/home.html'
    context_object_name = 'poules'

    # Set extra context data for user specific poules
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user.id
        user_poules = Poule.objects.filter(users__id=user)
        context['user_poules'] = user_poules
        return context


# CBV for new Poule, model is Poule
class PouleCreateView(LoginRequiredMixin, CreateView):
    model = Poule
    template_name = 'lobby/poule_form.html'
    fields = ['name', 'description', 'image', 'sport']

    # Override to set poule.admin to the current user
    def form_valid(self, form):
        form.instance.admin = self.request.user
        return super().form_valid(form)




