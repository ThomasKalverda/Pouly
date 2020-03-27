from django.db.models.signals import post_save, m2m_changed
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Score, Poule


@receiver(m2m_changed, sender=Poule.users.through)
def signal_function(sender, instance, action, **kwargs):
    if action == "post_add":
        score = Score(poule=instance, user_id=kwargs['pk_set'])
        score.save()


m2m_changed.connect(signal_function, sender=Poule.users.through)

