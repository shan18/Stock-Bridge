from django.contrib import admin
from .models import Company, InvestmentRecord, CompanyCMPRecord, Transaction, News


admin.site.register(Company)
admin.site.register(InvestmentRecord)
admin.site.register(CompanyCMPRecord)
admin.site.register(Transaction)
admin.site.register(News)
