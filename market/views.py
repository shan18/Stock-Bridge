from datetime import datetime
from decimal import Decimal

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.views import View
from django.views.generic import DetailView, ListView
from django.http import HttpResponseRedirect, HttpResponse, Http404, JsonResponse
from django.utils import timezone
from django.utils.timezone import localtime
from django.conf import settings
from django.urls import reverse
from django.db.models import Sum

from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Company, InvestmentRecord, Transaction, CompanyCMPRecord, News, UserNews
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
        return HttpResponse('cmp updated')


class MarketOverview(LoginRequiredMixin, CountNewsMixin, DetailView):
    template_name = 'market/overview.html'

    def get_object(self, *args, **kwargs):
        instance = Company.objects.all()
        if instance is None:
            raise Http404('No Companies registered Yet!')
        return instance

    def get_context_data(self, *args, **kwargs):
        context = super(MarketOverview, self).get_context_data(*args, **kwargs)
        qs = InvestmentRecord.objects.filter(user=self.request.user)
        context['investments'] = qs
        context['company_list'] = Company.objects.all()
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
                purchase_mode = request.POST.get('p-mode')
                price = company.cmp
                investment_obj, _ = InvestmentRecord.objects.get_or_create(user=user, company=company)
                total_quantity = investment_obj.stocks + quantity
                if purchase_mode == 'buy':
                    # Checking with max stocks a user can purchase for a company
                    if total_quantity <= company.max_stocks_sell:
                        purchase_amount = Decimal(quantity)*price
                        if user.cash >= purchase_amount:
                            if company.stocks_remaining >= quantity:
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
                elif purchase_mode == 'sell':
                    if quantity <= investment_obj.stocks and quantity <= company.stocks_offered:
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
                        messages.error(request, 'Please Enter a valid quantity!')
                else:
                    messages.error(request, 'Please select a valid purchase mode!')
            else:
                messages.error(request, 'Enter a valid quantity!')
        else:
            msg = 'The market is closed!'
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
