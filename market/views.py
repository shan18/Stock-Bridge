from django.shortcuts import render
from django.views import View
from django.views.generic import DetailView
from .models import Company, InvestmentRecord
from django.http import Http404
from stock_bridge.mixins import LoginRequiredMixin


class ProfileView(DetailView):
    template_name = 'market/profile.html'

    def get_object(self, *args, **kwargs):
        instance = Company.objects.all()
        if instance is None:
            raise Http404('No Companies registered Yet!')
        return instance

    def get_context_data(self,*args, **kwargs):
        context = super(ProfileView, self).get_context_data(*args, **kwargs)
        qs = Company.objects.all()
        context = {
            'companies':qs
        }

        return context


class CompanyTransactionView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        company_code = kwargs.get('code')
        company = Company.objects.get(code=company_code)
        obj, created = InvestmentRecord.objects.get_or_create(user=request.user, company=company)
        stocks_owned = obj.stocks
        context = {
            'object': company,
            'company_list': Company.objects.all(),
            'stocks_owned': stocks_owned
        }
        return render(request, 'market/transaction_market.html',context)

