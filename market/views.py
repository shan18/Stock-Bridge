from datetime import datetime
from decimal import Decimal

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views import View
from django.views.generic import ListView
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.utils import timezone
from django.utils.timezone import localtime
from django.conf import settings
from django.urls import reverse

from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Company, InvestmentRecord, Transaction, CompanyCMPRecord, News, UserNews, TransactionScheduler
from .forms import CompanyChangeForm
from stock_bridge.mixins import LoginRequiredMixin, AdminRequiredMixin, CountNewsMixin
from stocks.models import StocksDatabasePointer


User = get_user_model()

START_TIME = timezone.make_aware(getattr(settings, 'START_TIME'))
STOP_TIME = timezone.make_aware(getattr(settings, 'STOP_TIME'))


@login_required
def deduct_tax(request):
    if request.user.is_superuser:
        for user in User.objects.all():
            tax = user.cash * Decimal(0.4)
            user.cash -= tax
            user.save()
        return HttpResponse('success')
    return redirect('/')


class UpdateMarketView(LoginRequiredMixin, AdminRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        # update cmp
        StocksDatabasePointer.objects.get_pointer().increment_pointer()

        # scheduler
        schedule_qs = TransactionScheduler.objects.all()
        for query in schedule_qs:
            if query.perform_transaction(query.company.cmp):
                TransactionScheduler.objects.get(pk=query.pk).delete()
        
        pointer = StocksDatabasePointer.objects.get_pointer().pointer

        return HttpResponse('cmp updated - ' + str(pointer))


class MarketOverview(LoginRequiredMixin, CountNewsMixin, ListView):
    template_name = 'market/overview.html'
    queryset = Company.objects.all()

    def get_context_data(self, *args, **kwargs):
        context = super(MarketOverview, self).get_context_data(*args, **kwargs)
        context['investments'] = InvestmentRecord.objects.filter(user=self.request.user)
        return context


class CompanyAdminCompanyUpdateView(AdminRequiredMixin, CountNewsMixin, View):
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


class CompanyTransactionView(LoginRequiredMixin, CountNewsMixin, View):
    def get(self, request, *args, **kwargs):
        company_code = kwargs.get('code')
        company = Company.objects.get(code=company_code)
        obj, _ = InvestmentRecord.objects.get_or_create(user=request.user, company=company)
        stocks_owned = obj.stocks
        context = {
            'object': company,
            'company_list': Company.objects.all(),
            'stocks_owned': stocks_owned,
            'purchase_modes': ['buy', 'sell']
        }
        return render(request, 'market/transaction_market.html', context)

    def post(self, request, *args, **kwargs):
        """This method handles any post data at this page (primarily for transaction)"""
        company = Company.objects.get(code=kwargs.get('code'))
        current_time = timezone.make_aware(datetime.now())

        if START_TIME <= current_time <= STOP_TIME:
            user = request.user
            quantity = request.POST.get('quantity')

            if quantity != '' and int(quantity) > 0:
                quantity = int(quantity)
                mode = request.POST.get('mode')
                purchase_mode = request.POST.get('p-mode')
                price = company.cmp
                investment_obj, _ = InvestmentRecord.objects.get_or_create(user=user, company=company)
                if mode == 'transact':
                    if purchase_mode == 'buy':
                        purchase_amount = Decimal(quantity)*price
                        if user.cash >= purchase_amount:
                            _ = Transaction.objects.create(
                                user=user,
                                company=company,
                                num_stocks=quantity,
                                price=price,
                                mode=purchase_mode,
                                user_net_worth=InvestmentRecord.objects.calculate_net_worth(user)
                            )
                            messages.success(request, 'Transaction Complete!')
                        else:
                            messages.error(request, 'You have Insufficient Balance for this transaction!')
                    elif purchase_mode == 'sell':
                        if quantity <= investment_obj.stocks:
                            _ = Transaction.objects.create(
                                user=user,
                                company=company,
                                num_stocks=quantity,
                                price=price,
                                mode=purchase_mode,
                                user_net_worth=InvestmentRecord.objects.calculate_net_worth(user)
                            )
                            messages.success(request, 'Transaction Complete!')
                        else:
                            messages.error(request, 'You do not have that many stocks to sell!')
                    else:
                        messages.error(request, 'Please select a valid purchase mode!')
                elif mode == 'schedule':
                    schedule_price = request.POST.get('price')
                    if purchase_mode == 'buy':
                        _ = TransactionScheduler.objects.create(
                            user=user,
                            company=company,
                            num_stocks=quantity,
                            price=schedule_price,
                            mode=purchase_mode
                        )
                        messages.success(request, 'Request Submitted!')
                    elif purchase_mode == 'sell':
                        _ = TransactionScheduler.objects.create(
                            user=user,
                            company=company,
                            num_stocks=quantity,
                            price=schedule_price,
                            mode=purchase_mode
                        )
                        messages.success(request, 'Request Submitted!')
                    else:
                        messages.error(request, 'Please select a valid purchase mode!')
                else:
                    messages.error(request, 'Please select a valid transaction mode!')
            else:
                messages.error(request, 'Enter a valid quantity!')
        else:
            # msg = 'The market is closed!'
            msg = 'The market will be live tomorrow from 9:30 PM'
            messages.info(request, msg)
        url = reverse('market:transaction', kwargs={'code': company.code})
        if request.is_ajax():
            return JsonResponse({'next_path': url})
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


class NewsView(LoginRequiredMixin, CountNewsMixin, View):
    template_name = 'market/news.html'
    url = 'news'

    def get(self, request, *args, **kwargs):
        UserNews.objects.get_by_user(request.user).update(read=True)
        queryset = News.objects.filter(is_active=True)
        return render(request, 'market/news.html', {'object_list': queryset})
