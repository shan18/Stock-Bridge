import logging
from datetime import datetime
from decimal import Decimal

from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.views import View
from django.views.generic import DetailView
from django.http import Http404
from django.utils import timezone
from django.utils.timezone import localtime
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Company, InvestmentRecord, Transaction, CompanyCMPRecord
from .forms import StockTransactionForm, CompanyChangeForm
from stock_bridge.mixins import LoginRequiredMixin, AdminRequiredMixin


User = get_user_model()

START_TIME = timezone.make_aware(getattr(settings, 'START_TIME'))
STOP_TIME = timezone.make_aware(getattr(settings, 'STOP_TIME'))


class MarketOverview(LoginRequiredMixin, DetailView):
    template_name = 'market/overview.html'

    def get_object(self, *args, **kwargs):
        instance = Company.objects.all()
        if instance is None:
            raise Http404('No Companies registered Yet!')
        return instance

    def get_context_data(self,*args, **kwargs):
        context = super(MarketOverview, self).get_context_data(*args, **kwargs)
        qs = Company.objects.all()
        context = {
            'companies':qs
        }

        return context


@login_required
def deduct_tax(request):
    if request.user.is_superuser:
        for user in User.objects.all():
            tax = user.cash * Decimal(0.4)
            user.cash -= tax
            user.save()
        return HttpResponse('success')
    return redirect('/')


@login_required
def update_market(request):
    if request.user.is_superuser:
        company_qs = Company.objects.all()
        for company in company_qs:
            company.update_cmp()
            obj = CompanyCMPRecord.objects.create(company=company, cmp=company.cmp)
        return HttpResponse('cmp updated')
    return redirect('/')


class CompanyAdminCompanyUpdateView(AdminRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        company = Company.objects.get(code=kwargs.get('code'))
        return render(request, 'market/admin_company_change.html', {
            'object': company,
            'company_list': Company.objects.all(),
            'form': CompanyChangeForm()
        })

    def post(self, request, *args, **kwargs):
        company = Company.objects.get(code=kwargs.get('code'))
        price = request.POST.get('price')
        old_price = company.cmp
        company.cmp = Decimal(int(price))
        company.save()
        company.calculate_change(old_price)
        print('price', int(price))
        url = reverse('market:admin', kwargs={'code': company.code})
        return HttpResponseRedirect(url)


class CompanyCMPCreateView(View):
    def get(self, request, *args, **kwargs):
        for company in Company.objects.all():
            obj = CompanyCMPRecord.objects.create(company=company, cmp=company.cmp)
        return HttpResponse('success')


class CompanyTransactionView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        company_code = kwargs.get('code')
        company = Company.objects.get(code=company_code)
        obj, created = InvestmentRecord.objects.get_or_create(user=request.user, company=company)
        stocks_owned = obj.stocks
        max_stocks_sell = company.max_stocks_sell
        stock_percentage = (stocks_owned/max_stocks_sell)*100
        percentage_difference = 100-stock_percentage
        difference = max_stocks_sell - stocks_owned
        context = {
            'object': company,
            'company_list': Company.objects.all(),
            'stocks_owned': stocks_owned,
            'stock_percentage':stock_percentage,
            'difference':difference,
            'percentage_difference':percentage_difference,
            'form': StockTransactionForm()
        }
        return render(request, 'market/transaction_market.html',context)

    def post(self, request, *args, **kwargs):
        """This method handles any post data at this page (primarily for transaction)"""
        company = Company.objects.get(code=kwargs.get('code'))
        current_time = timezone.make_aware(datetime.now())

        if START_TIME <= current_time <= STOP_TIME:
            user = request.user
            mode = request.POST.get('mode')
            quantity = int(request.POST.get('quantity'))
            price = company.cmp
            investment_obj, obj_created = InvestmentRecord.objects.get_or_create(user=user, company=company)

            if quantity > 0:
                if mode == 'buy':
                    # Checking with max stocks a user can purchase for a company
                    total_quantity = investment_obj.stocks + quantity
                    if total_quantity <= company.max_stocks_sell:
                        purchase_amount = Decimal(quantity)*price
                        if user.cash >= purchase_amount:
                            if company.stocks_remaining >= quantity:
                                obj = Transaction.objects.create(
                                    user=user,
                                    company=company,
                                    num_stocks=quantity,
                                    price=price,
                                    mode=mode,
                                    user_net_worth=InvestmentRecord.objects.calculate_net_worth(user)
                                )

                                messages.success(request, 'Transaction Complete!')

                            else:
                                messages.error(
                                    request, 'The company has only {} stocks left!'.format(company.stocks_remaining)
                                )

                        else:
                            messages.error(request, 'You have Insufficient Balance for this transaction!')
                    else:
                        messages.error(
                            request,
                            'This company allows each user to hold a maximum of {} stocks'.format(
                                company.max_stocks_sell
                            )
                        )

                elif mode == 'sell':
                    if quantity <= investment_obj.stocks and quantity <= company.stocks_offered:
                        obj = Transaction.objects.create(
                            user=user,
                            company=company,
                            num_stocks=quantity,
                            price=price,
                            mode=mode,
                            user_net_worth=InvestmentRecord.objects.calculate_net_worth(user)
                        )

                        messages.success(request, 'Transaction Complete!')

                    else:
                        messages.error(request, 'Please Enter a valid quantity!')

                else:
                    messages.error(request, 'Please enter a valid mode!')

            else:
                messages.error(request, 'The Quantity cannot be negative!')

        else:
            msg = 'The market is closed!'
            messages.info(request, msg)
        url = reverse('market:transaction', kwargs={'code': company.code})
        return HttpResponseRedirect(url)


# For Chart
class CompanyCMPChartData(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, format=None, *args, **kwargs):
        qs = CompanyCMPRecord.objects.filter(company__code=kwargs.get('code'))
        if qs.count() > 15:
            qs = qs[:15]
        qs = reversed(qs)
        labels = []
        cmp_data = []
        for cmp_record in qs:
            labels.append(localtime(cmp_record.timestamp).strftime('%H:%M'))
            cmp_data.append(cmp_record.cmp)
        current_cmp = Company.objects.get(code=kwargs.get('code')).cmp
        if cmp_data[-1] != current_cmp:
            labels.append(timezone.make_aware(datetime.now()).strftime('%H:%M'))
            cmp_data.append(current_cmp)

        data = {
            "labels": labels,
            "cmp_data": cmp_data,
        }
        return Response(data)

