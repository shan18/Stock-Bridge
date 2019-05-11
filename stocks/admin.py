from django.contrib import admin

from .models import StocksDatabase, StocksDatabasePointer


class StocksDatabaseAdmin(admin.ModelAdmin):
    list_display = ('company', 'pointer', 'price')
    search_fields = ['company', 'pointer']
    ordering = ('company', 'pointer', 'price')

    class Meta:
        model = StocksDatabase

admin.site.register(StocksDatabase, StocksDatabaseAdmin)


admin.site.register(StocksDatabasePointer)
