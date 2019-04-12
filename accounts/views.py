from django.shortcuts import redirect
from django.contrib import messages
from django.views.generic import FormView, CreateView, DetailView
from django.utils.safestring import mark_safe
from market.models import Company
from .forms import LoginForm, RegisterForm
from stock_bridge.mixins import (
    AnonymousRequiredMixin,
    RequestFormAttachMixin,
    NextUrlMixin,
    LoginRequiredMixin
)


class LoginView(AnonymousRequiredMixin, RequestFormAttachMixin, NextUrlMixin, FormView):
    form_class = LoginForm
    template_name = 'accounts/login.html'
    success_url = '/'
    default_url = '/'
    default_next = '/'

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

    def form_valid(self, form):
        super(RegisterView, self).form_valid(form)
        messages.success(self.request, 'Verification link sent! Please check your email.')
        return redirect(self.success_url)
