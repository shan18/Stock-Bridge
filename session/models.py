from django.conf import settings
from django.db import models


User = settings.AUTH_USER_MODEL


class LoggedInUser(models.Model):
    """ Model to store the list of logged in users """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    session_key = models.CharField(max_length=32, null=True, blank=True)  # session key is 32 characters long

    def __str__(self):
        return self.user.username
