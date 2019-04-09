from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserManager(BaseUserManager):

    def create_user(self, username, email, password=None, full_name=None, is_active=True, is_staff=False, is_superuser=False):
        if not username:
            raise ValueError('Users must have a unique username.')
        if not email:
            raise ValueError('Users must have an email.')
        if not password:
            raise ValueError('Users must have a password.')

        user_obj = self.model(
            username=username,
            email=self.normalize_email(email),
            full_name=full_name
        )
        user_obj.set_password(password)
        user_obj.is_active = is_active
        user_obj.staff = is_staff
        user_obj.is_superuser = is_superuser
        user_obj.cash = 0.00
        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self, username, email, full_name=None, password=None):
        user = self.create_user(
            username,
            email,
            password=password,
            full_name=full_name,
            is_staff=True
        )
        return user

    def create_superuser(self, username, email, full_name=None, password=None):
        user = self.create_user(
            username,
            email,
            password=password,
            full_name=full_name,
            is_staff=True,
            is_superuser=True
        )
        return user


class User(AbstractBaseUser):
    username = models.CharField(unique=True, max_length=120)
    email = models.EmailField(unique=True, max_length=255)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    def __str__(self):
        return self.username

    def get_full_name(self):
        if self.full_name:
            return self.full_name
        return self.email

    def get_short_name(self):
        return self.username

    def has_perm(self, perm, object=None):
        """ Does the user have a specific permission? """
        return True

    def has_module_perms(self, app_label):
        """ Does the user have permissions to view the app 'app_label'? """
        return True

    @property
    def is_staff(self):
        return self.staff
