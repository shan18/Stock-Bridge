from django.contrib import admin
from .models import Company, InvestmentRecord, CompanyCMPRecord, Transaction, News, UserNews, TransactionScheduler


admin.site.register(Company)


class InvestmentRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'stocks')
    search_fields = ['user', 'company']
    ordering = ('user', 'company')

    class Meta:
        model = InvestmentRecord

admin.site.register(InvestmentRecord, InvestmentRecordAdmin)


class CompanyCMPRecordAdmin(admin.ModelAdmin):
    list_display = ('company', 'cmp', 'timestamp')
    search_fields = ['company']
    ordering = ('company', 'timestamp')

    class Meta:
        model = CompanyCMPRecord

admin.site.register(CompanyCMPRecord, CompanyCMPRecordAdmin)


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'num_stocks', 'price', 'mode', 'timestamp')
    search_fields = ['user', 'company']
    ordering = ('user', 'company', 'mode', 'timestamp')

    class Meta:
        model = Transaction

admin.site.register(Transaction, TransactionAdmin)


class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active')
    search_fields = ['title']
    ordering = ('title', 'is_active')

    class Meta:
        model = News

admin.site.register(News, NewsAdmin)


class UserNewsAdmin(admin.ModelAdmin):
    list_display = ('user', 'news', 'read')
    search_fields = ['user', 'news']
    ordering = ('user', 'news', 'read')

    class Meta:
        model = UserNews

admin.site.register(UserNews, UserNewsAdmin)


class TransactionSchedulerAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'num_stocks', 'price', 'mode', 'timestamp')
    search_fields = ['user', 'company', 'mode']
    ordering = ('user', 'company', 'mode', 'price', 'timestamp')

    class Meta:
        model = TransactionScheduler

admin.site.register(TransactionScheduler, TransactionSchedulerAdmin)
