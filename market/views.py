from django.shortcuts import render
from django.views import View
from django.views.generic import DetailView
from .models import Company, InvestmentRecord, Transaction
from django.http import Http404
from stock_bridge.mixins import LoginRequiredMixin
from .forms import StockTransactionForm
from datetime import datetime
from django.utils import timezone
from django.conf import settings
from decimal import Decimal
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect

START_TIME = timezone.make_aware(getattr(settings, 'START_TIME'))
STOP_TIME = timezone.make_aware(getattr(settings, 'STOP_TIME'))


class ProfileView(LoginRequiredMixin, DetailView):
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
            'stocks_owned': stocks_owned,
            'form': StockTransactionForm()
        }
        return render(request, 'market/transaction_market.html',context)

    def post(self, request, *args, **kwargs):
        '''This method handles any post data at this page (primarily for transaction)'''
        company = Company.objects.get(code=kwargs.get('code'))
        current_time = timezone.make_aware(datetime.now())

        if current_time >= START_TIME and current_time <= STOP_TIME:
            user = request.user
            mode = request.POST.get('mode')
            quantity = int(request.POST.get('quantity'))
            price = company.cmp
            investment_obj, obj_created = InvestmentRecord.objects.get_or_create(user=user, company=company)

            if quantity > 0:
                if mode == 'buy':
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
                            messages.error(request, 'The company does not have that many stocks left!')

                    else:
                        messages.error(request, 'You have Insufficient Balance for this transaction!')

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


