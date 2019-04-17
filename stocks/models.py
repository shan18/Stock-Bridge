from django.db import models

from market.models import Company


class StocksDatabasePointer(models.Model):
    pointer = models.IntegerField(default=0)

    def __str__(self):
        return 'stocks_database_pointer'


class StocksDatabase(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    pointer = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)

    class Meta:
        ordering = ['company', 'pointer']

    def __str__(self):
        return self.company.name + ' - ' + str(self.pointer)
