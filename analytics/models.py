from django.conf import settings
from django.contrib.sessions.models import Session
from django.db import models
from django.db.models.signals import post_save

from .utils import get_client_ip
from accounts.signals import user_session_signal


User = settings.AUTH_USER_MODEL

# To disable the post_save connectors
FORCE_ONE_SESSION = getattr(settings, 'FORCE_ONE_SESSION', False)
FORCE_INACTIVE_USER_END_SESSION = getattr(settings, 'FORCE_INACTIVE_USER_END_SESSION', False)


class UserSessionQuerySet(models.query.QuerySet):
    def delete_inactive(self):
        self.filter(Q(active=False) | Q(ended=True)).delete()


class UserSessionManager(models.Manager):
    def get_queryset(self):
        return UserSessionQuerySet(self.model, using=self._db)

    def delete_inactive(self):
        self.get_queryset().delete_inactive()


class UserSession(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, on_delete=True)
    ip_address = models.CharField(max_length=220, blank=True, null=True)
    session_key = models.CharField(max_length=100, blank=True, null=True)  # min length 50
    timestamp = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)  # session active
    ended = models.BooleanField(default=False)  # session ended --> logged out

    objects = UserSessionManager()

    def __str__(self):
        return self.user.email

    def end_session(self):
        try:
            Session.objects.get(pk=self.session_key).delete()
            self.ended = True
            self.active = False
            self.save()
        except Exception as e:
            print(e)
        return self.ended


def user_session_receiver(sender, instance, request, *args, **kwargs):
    UserSession.objects.create(
        user=instance,
        ip_address=get_client_ip(request),
        session_key=request.session.session_key  # Django 1.11
    )


user_session_signal.connect(user_session_receiver)


def post_save_session_receiver(sender, instance, created, *args, **kwargs):
    if created:
        # When user logs in, delete all the sessions related to the user except the current one
        qs = UserSession.objects.filter(user=instance.user).exclude(id=instance.id)
        qs.update(active=False, ended=True)

    if not instance.active and not instance.ended:
        instance.end_session()


if FORCE_ONE_SESSION:
    post_save.connect(post_save_session_receiver, sender=UserSession)


def post_save_user_changed_receiver(sender, instance, created, *args, **kwargs):
    if not created:
        # if user becomes inactive, delete all of its inactive sessions
        if not instance.is_active:
            qs = UserSession.objects.filter(user=instance, ended=False)
            qs.update(active=False, ended=True)
            # for session in qs:
            #     session.end_session()
            UserSession.objects.filter(user=instance).delete_inactive()


if FORCE_INACTIVE_USER_END_SESSION:
    post_save.connect(post_save_user_changed_receiver, sender=User)
