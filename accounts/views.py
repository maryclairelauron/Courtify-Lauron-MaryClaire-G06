from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from .forms import RegisterForm
from .models import User


def redirect_url_for(user):
    if user.role == User.Role.ADMIN:
        return '/accounts/admin-dashboard/'
    return '/accounts/customer-dashboard/'


def register_view(request):
    if request.user.is_authenticated:
        return redirect(redirect_url_for(request.user))
    form = RegisterForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Account created! You can now log in.")
            return redirect('accounts:login')
        messages.error(request, "Please fix the errors below.")
    return render(request, 'accounts/register.html', {'form': form})


class CourtifyLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return redirect_url_for(self.request.user)

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password.")
        return super().form_invalid(form)