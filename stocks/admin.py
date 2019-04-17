from django.contrib import admin

from .models import StocksDatabase, StocksDatabasePointer


admin.site.register(StocksDatabasePointer)
admin.site.register(StocksDatabase)
