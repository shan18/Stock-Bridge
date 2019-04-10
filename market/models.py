from django.db import models

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







