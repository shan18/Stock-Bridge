from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save, post_save
from django.urls import reverse
from decimal import Decimal

User = get_user_model()


TRANSACTION_MODES = (
    ('buy', 'BUY'),
    ('sell', 'SELL')
)

CAP_TYPES = (
    ('small', 'Small Cap'),
    ('mid', 'Mid Cap'),
    ('large', 'Large Cap'),
)


class Company(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=20, unique=True)
    cap = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    cmp = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    change = models.DecimalField(max_digits=10, decimal_places=2,default=0.00)
    stocks_offered = models.IntegerField(default=0)
    stocks_remaining = models.IntegerField(default=stocks_offered)
    cap_type = models.CharField(max_length=20, choices=CAP_TYPES, blank=True, null=True)
    industry = models.CharField(max_length=120, blank=True, null=True)
    temp_stocks_bought = models.IntegerField(default=0)
    temp_stocks_sold = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['cap_type', 'code']

    def __str__(self):
        return self.name

    def get_cap(self):
        cap_type = self.cap_type
        if cap_type=='small':
            return 'Small Cap'
        elif cap_type=='mid':
            return 'Mid Cap'
        return 'Large Cap'

    def get_absolute_url(self):
        return reverse('market:transaction',kwargs={'code':self.code})


def pre_save_company_receiver(sender, instance, *args, **kwargs):
    if instance.cmp <= Decimal(0.00):
        instance.cmp = Decimal(0.01)


pre_save.connect(pre_save_company_receiver, sender=Company)


def post_save_company_receiver(sender, instance, created, *args, **kwargs):
    if created:
        user_qs = User.objects.all()
        for user in user_qs:
            obj, create= InvestmentRecord.objects.get_or_create(user=user, company=instance)


post_save.connect(post_save_company_receiver, sender=Company)


class InvestmentRecordQueryset(models.query.QuerySet):
    def get_by_user(self, user):
        return self.filter(user=user)

    def get_by_company(self, company):
        return self.filter(company=company)


class InvestmentRecordManager(models.Manager):
    def get_queryset(self):
        return InvestmentRecordQueryset(self.model, self._db)

    def get_by_user(self, user):
        return self.get_queryset().get_by_user(user=user)

    def get_by_company(self, company):
        return self.get_queryset().get_by_company(company=company)


class InvestmentRecord(models.Model):
    user = models.ForeignKey(User, on_delete=True)
    company = models.ForeignKey(Company, on_delete=True)
    stocks = models.IntegerField(default=0)
    updated = models.DateTimeField(auto_now=True)

    objects = InvestmentRecordManager()

    class Meta:
        unique_together = ('user', 'company')

    def __str__(self):
        return self.user.username + ' - ' + self.company.code


def post_save_user_create_receiver(sender, instance, created, *args, **kwargs):
    '''For every user created'''
    if created:
        '''It will create user's investment record with all the companies'''
        for company in Company.objects.all():
            obj = InvestmentRecord.objects.create(user=instance, company=company)


post_save.connect(post_save_user_create_receiver, sender=User)


class CompanyCMPRecord(models.Model):
    company = models.ForeignKey(Company, on_delete=True)
    cmp = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return self.company.code

