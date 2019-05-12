from datetime import datetime

from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, DetailView, FormView, CreateView, DeleteView, View
from django.views.generic.edit import FormMixin
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.urls import reverse, reverse_lazy

from .forms import LoginForm, RegisterForm, ReactivateEmailForm
from .models import EmailActivation
from market.models import InvestmentRecord, TransactionScheduler
from stock_bridge.mixins import (
    AnonymousRequiredMixin,
    RequestFormAttachMixin,
    NextUrlMixin,
    LoginRequiredMixin,
    CountNewsMixin
)


User = get_user_model()

START_TIME = timezone.make_aware(getattr(settings, 'START_TIME'))
STOP_TIME = timezone.make_aware(getattr(settings, 'STOP_TIME'))
BOTTOMLINE_CASH = getattr(settings, 'BOTTOMLINE_CASH', 1000)
MAX_LOAN_ISSUE = getattr(settings, 'MAX_LOAN_ISSUE', 1000)


@login_required
def close_bank(request):
    """ Deduct Interest and cancel loan """
    if request.user.is_superuser:
        for user in User.objects.all():
            user.cancel_loan()
            user.deduct_interest()
        return HttpResponse('Bank Closed', status=200)
    return redirect('home')


@login_required
def cancel_loan(request):
    """ Deduct entire loan amount from user's balance """
    if request.user.is_superuser:
        for user in User.objects.all():
            user.cancel_loan()
        return HttpResponse('Loan Deducted', status=200)
    return redirect('home')


@login_required
def deduct_interest(request):
    """ Deduct interest from user's balance """
    if request.user.is_superuser:
        for user in User.objects.all():
            user.deduct_interest()
        return HttpResponse('Interest Deducted', status=200)
    return redirect('home')


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


class LeaderBoardView(CountNewsMixin, View):
    template_name = 'accounts/leaderboard.html'

    def get(self, request, *args, **kwargs):
        data = []
        user_qs = User.objects.all()
        for user in user_qs:
            net_worth = InvestmentRecord.objects.calculate_net_worth(user)
            data.append((user.username, user.full_name, net_worth, user.coeff_of_variation))
        data = sorted(data, key=lambda d: (-d[2], d[3]))
        
        # Obtain data and rank of current user
        current_user_data = []
        rank_count = 1
        for user_data in data:
            if user_data[0] == self.request.user.username:
                current_user_data.append((user_data, rank_count))
            rank_count += 1
        return render(request, 'accounts/leaderboard.html', {'data': data, 'current_user': current_user_data})


class LoanView(LoginRequiredMixin, CountNewsMixin, View):

    def get(self, request, *args, **kwargs):
        return render(request, 'accounts/loan.html', {
            'user': request.user
        })

    def post(self, request, *args, **kwargs):
        current_time = timezone.make_aware(datetime.now())
        if current_time >= START_TIME and current_time <= STOP_TIME:
            mode = request.POST.get('mode')
            user = request.user
            if mode == 'issue':
                decision = user.issue_loan()
                if decision == 'success':
                    messages.success(request, 'Loan issued.')
                elif decision == 'loan_count_exceeded':
                    messages.error(
                        request,
                        'Loan can be issued only {max_issue} times in a day!'.format(max_issue=MAX_LOAN_ISSUE)
                    )
                elif decision == 'bottomline_not_reached':
                    messages.error(
                        request,
                        'Cash must be less than {bottom_line} to issue a loan. Your current balance: {cash}'.format(
                            bottom_line=BOTTOMLINE_CASH,
                            cash=user.cash
                        )
                    )
                else:
                    messages.error(request, 'Cannot Issue loan right now.')
            elif mode == 'pay':
                repay_amount = int(request.POST.get('repay_amount'))
                if user.loan <= 0:
                    messages.error(request, "You have no pending loan!")
                elif user.loan > 0:
                    if repay_amount <= 0 or repay_amount > user.cash:
                        messages.error(request, 'Please enter a valid amount.')
                    elif user.pay_installment(repay_amount):
                        messages.success(request, 'Installment paid!')
                    else:
                        messages.error(
                            request,
                            'You should have sufficient balance!'
                        )
        else:
            msg = 'The market is closed!'
            messages.info(request, msg)
        
        if request.is_ajax():
            return JsonResponse({'next_path': reverse('account:loan')})

        return redirect('account:loan')


class AccountEmailActivateView(FormMixin, View):
    success_url = '/login/'
    form_class = ReactivateEmailForm
    key = None

    def get(self, request, key=None, *args, **kwargs):
        self.key = key
        if key is not None:
            qs = EmailActivation.objects.filter(key__iexact=key)
            confirm_qs = qs.confirmable()
            if confirm_qs.count() == 1:  # Not confirmed but confirmable
                obj = confirm_qs.first()
                obj.activate()
                messages.success(request, 'Your email has been confirmed! Please login to continue.')
                return redirect('login')
            else:
                activated_qs = qs.filter(activated=True)
                if activated_qs.exists():
                    # reset_link = reverse('password_reset')
                    # msg = """Your email has already been confirmed.
                    # Do you want to <a href="{link}">reset you password</a>?""".format(link=reset_link)
                    # messages.success(request, mark_safe(msg))
                    return redirect('login')
        context = {'form': self.get_form(), 'key': key}  # get_form() works because of the mixin
        return render(request, 'registration/activation_error.html', context)

    def post(self, request, *args, **kwargs):
        # create a form to receive an email
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        msg = 'Activation link sent. Please check your email.'
        messages.success(self.request, msg)
        email = form.cleaned_data.get('email')
        obj = EmailActivation.objects.email_exists(email).first()
        user = obj.user
        new_activation = EmailActivation.objects.create(user=user, email=email)
        new_activation.send_activation()
        return super(AccountEmailActivateView, self).form_valid(form)

    def form_invalid(self, form):
        """
        This method had to be explicitly written because this view uses the basic django "View" class.
        If it had used some other view like ListView etc. Django would have handled it automatically.
        """
        context = {'form': form, 'key': self.key}
        return render(self.request, 'registration/activation_error.html', context)


class LoginView(AnonymousRequiredMixin, RequestFormAttachMixin, NextUrlMixin, FormView):
    form_class = LoginForm
    template_name = 'accounts/login.html'
    success_url = '/'
    default_url = '/'
    default_next = '/'

    def get_context_data(self, *args, **kwargs):
        context = super(LoginView, self).get_context_data(*args, **kwargs)
        context['heading'] = 'Login'
        context['button_text'] = 'Sign In'
        return context

    def form_valid(self, form):
        request = self.request
        response = form.cleaned_data
        if not response.get('success'):
            messages.warning(request, mark_safe(response.get('message')))
            return redirect('login')
        next_path = self.get_next_url()
        return redirect(next_path)


class RegisterView(AnonymousRequiredMixin, CreateView):
    form_class = RegisterForm
    template_name = 'accounts/register.html'
    success_url = '/login/'

    def get_context_data(self, *args, **kwargs):
        context = super(RegisterView, self).get_context_data(*args, **kwargs)
        context['heading'] = 'Register'
        context['button_text'] = 'Sign Up'
        return context

    def form_valid(self, form):
        super(RegisterView, self).form_valid(form)
        print(form.cleaned_data)
        messages.success(self.request, 'Verification link sent! Please check your email.')
        return redirect(self.success_url)


class ProfileView(LoginRequiredMixin, CountNewsMixin, DetailView):
    template_name = 'accounts/profile.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.username != kwargs.get('username'):
            return redirect('/')
        return super(ProfileView, self).dispatch(request, *args, **kwargs)

    def get_object(self, *args, **kwargs):
        username = self.kwargs.get('username')
        instance = User.objects.filter(username=username).first()
        if instance is None:
            return Http404('User not found')
        return instance

    def get_context_data(self, *args, **kwargs):
        context = super(ProfileView, self).get_context_data(*args, **kwargs)
        qs = InvestmentRecord.objects.filter(user=self.request.user)
        if qs.count() >= 1:
            context['net_worth'] = InvestmentRecord.objects.calculate_net_worth(self.request.user)
            context['investments'] = qs
        return context


class ScheduleView(LoginRequiredMixin, CountNewsMixin, ListView):
    template_name = 'accounts/schedules.html'

    def get_queryset(self):
        return TransactionScheduler.objects.get_by_user(self.request.user)


class ScheduleDeleteView(LoginRequiredMixin, DeleteView):

    def get_object(self, **kwargs):
        print(self.kwargs)
        obj = TransactionScheduler.objects.get(pk=self.kwargs.get('pk'))
        return obj

    def get_success_url(self):
        return reverse_lazy('account:schedules', kwargs={'username': self.request.user.username})
