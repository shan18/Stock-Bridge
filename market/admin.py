from django.contrib import admin
from .models import Company, InvestmentRecord, CompanyCMPRecord
# Register your models here.
admin.site.register(Company)
admin.site.register(InvestmentRecord)
admin.site.register(CompanyCMPRecord)