import random
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
    cap_type = models.CharField(max_length=20, choices=CAP_TYPES, blank=True, null=True)
    stocks_bought = models.IntegerField(default=0)
    industry = models.CharField(max_length=120, blank=True, null=True)
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

    def user_buy_stocks(self, quantity):
        self.stocks_bought += quantity
        self.save()

    def user_sell_stocks(self, quantity):
        if quantity <= self.stocks_bought:
            self.stocks_bought -= quantity
            self.save()
            return True
        return False

    def calculate_change(self, new_price):
        self.change = ((new_price - self.cmp) / self.cmp) * Decimal(100.00)
        self.save()

    def update_cmp(self, new_price):
        self.calculate_change(new_price)
        self.cmp = new_price
        self.save()


def post_save_company_receiver(sender, instance, created, *args, **kwargs):
    if created:
        # Create Investment Records of the company with each existing user
        user_qs = User.objects.all()
        for user in user_qs:
            obj, create= InvestmentRecord.objects.get_or_create(user=user, company=instance)
        
        # Create CMP Record of the company
        CompanyCMPRecord.objects.create(company=instance, cmp=instance.cmp)


post_save.connect(post_save_company_receiver, sender=Company)


class TransactionQueryset(models.query.QuerySet):
    def get_by_user(self, user):
        return self.filter(user=user)

    def get_by_company(self, company):
        return self.filter(company=company)

    def get_by_user_and_company(self, user, company):
        return self.filter(user=user, company=company)


class TransactionManager(models.Manager):
    def get_queryset(self):
        return TransactionQueryset(self.model, using=self._db)

    def get_by_user(self, user):
        return self.get_queryset().get_by_user(user=user)

    def get_by_company(self, company):
        return self.get_queryset().get_by_company(company=company)

    def get_by_user_and_company(self, user, company):
        return self.get_queryset().get_by_user_and_company(user=user, company=company)


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    num_stocks = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    mode = models.CharField(max_length=10, choices=TRANSACTION_MODES)
    user_net_worth = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = TransactionManager()

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return '{user} - {company}'.format(
            user=self.user.username, company=self.company.name
        )


def pre_save_transaction_receiver(sender, instance, *args, **kwargs):
    amount = InvestmentRecord.objects.calculate_net_worth(instance.user)
    instance.user_net_worth = amount

    investment_obj , obj_created = InvestmentRecord.objects.get_or_create(
        user=instance.user,
        company=instance.company
    )

    if instance.mode == 'buy':
        instance.user.buy_stocks(instance.num_stocks, instance.price)
        instance.company.user_buy_stocks(instance.num_stocks)
        investment_obj.add_stocks(instance.num_stocks)
    elif instance.mode == 'sell':
        instance.user.sell_stocks(instance.num_stocks, instance.price)
        instance.company.user_sell_stocks(instance.num_stocks)
        investment_obj.reduce_stocks(instance.num_stocks)


pre_save.connect(pre_save_transaction_receiver, sender=Transaction)


def post_save_transaction_create_receiver(sender, instance, created, *args, **kwargs):
    if created:
        net_worth_list = [
            instance.user_net_worth for transaction in Transaction.objects.get_by_user(instance.user)
        ]

        instance.user.update_cv(net_worth_list)


post_save.connect(post_save_transaction_create_receiver, sender=Transaction)


class TransactionSchedulerQueryset(models.query.QuerySet):
    def get_by_user(self, user):
        return self.filter(user=user)

    def get_by_company(self, company):
        return self.filter(company=company)


class TransactionSchedulerManager(models.Manager):
    def get_queryset(self):
        return TransactionQueryset(self.model, using=self._db)

    def get_by_user(self, user):
        return self.get_queryset().get_by_user(user)

    def get_by_company(self, company):
        return self.get_queryset().get_by_company(company)


class TransactionScheduler(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    num_stocks = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    mode = models.CharField(max_length=10, choices=TRANSACTION_MODES)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = TransactionSchedulerManager()

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return '{user}: {company} - {stocks}: {price} - {mode}'.format(
            user=self.user.username, company=self.company.name, stocks=self.num_stocks, price=self.price, mode=self.mode
        )

    def get_absolute_url(self):
        return reverse('schedules', kwargs={'username':self.user.username})

    def validate_by_price(self, price):
        if (
            self.mode == 'buy' and price <= self.price and price * Decimal(self.num_stocks) <= self.user.cash
        ) or (self.mode == 'sell' and price >= self.price):
            return True
        return False
    
    def validate_by_stocks(self):
        invested_stocks = InvestmentRecord.objects.get(user=self.user, company=self.company).stocks
        if self.mode == 'buy' or (self.mode == 'sell' and self.num_stocks <= invested_stocks):
            return True
        return False
    
    def perform_transaction(self, price):
        if self.validate_by_price(price) and self.validate_by_stocks():
            Transaction.objects.create(
                user=self.user,
                company=self.company,
                num_stocks=self.num_stocks,
                price=price,
                mode=self.mode
            )
            return True
        return False


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

    def calculate_net_worth(self, user):
        qs = self.get_by_user(user)
        amount = Decimal(0.00)
        for inv in qs:
            amount += Decimal(inv.stocks) * inv.company.cmp
        return amount + user.cash


class InvestmentRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    stocks = models.IntegerField(default=0)
    updated = models.DateTimeField(auto_now=True)

    objects = InvestmentRecordManager()

    class Meta:
        unique_together = ('user', 'company')

    def __str__(self):
        return self.user.username + ' - ' + self.company.code

    def add_stocks(self, num_stocks):
        self.stocks += num_stocks
        self.save()

    def reduce_stocks(self, num_stocks):
        if self.stocks >= num_stocks:
            self.stocks -= num_stocks
            self.save()


def post_save_user_investment_create_receiver(sender, instance, created, *args, **kwargs):
    """ For every user created """
    if created:
        """It will create user's investment record with all the companies"""
        for company in Company.objects.all():
            obj = InvestmentRecord.objects.create(user=instance, company=company)


post_save.connect(post_save_user_investment_create_receiver, sender=User)


class CompanyCMPRecord(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    cmp = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return self.company.code


class News(models.Model):
    title = models.CharField(max_length=120)
    content = models.TextField()
    is_active = models.BooleanField(default=True)  # Inactive news won't appear in dashboard
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp', '-updated']

    def __str__(self):
        return self.title


def post_save_news_create_receiver(sender, instance, created, *args, **kwargs):
    if created:
        for user in User.objects.all():
            UserNews.objects.create(user=user, news=instance)
    else:
        UserNews.objects.get_by_news(news=instance).update(read=not instance.is_active)


post_save.connect(post_save_news_create_receiver, sender=News)


def post_save_user_news_create_receiver(sender, instance, created, *args, **kwargs):
    if created:
        instance.news_count = News.objects.filter(is_active=True).count()
        instance.save()


post_save.connect(post_save_user_news_create_receiver, sender=User)


class UserNewsManager(models.Manager):
    def get_by_user(self, user):
        return self.get_queryset().filter(user=user)
    
    def get_by_news(self, news):
        return self.get_queryset().filter(news=news)


class UserNews(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    news = models.ForeignKey(News, on_delete=models.CASCADE)
    read = models.BooleanField(default=False)

    objects = UserNewsManager()

    def __str__(self):
        return self.news.title + ' - ' + self.user.username
