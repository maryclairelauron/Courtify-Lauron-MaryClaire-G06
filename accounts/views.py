from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect

from .forms import RegisterForm, ProfileForm
from .models import User


def dashboard_name_for(user):
    if user.role == User.Role.ADMIN:
        return 'accounts:admin_dashboard'
    return 'accounts:customer_dashboard'


def role_required(role):
    """Only lets logged-in users with the given role open the view."""
    def decorator(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            if request.user.role != role:
                messages.error(request, "You are not allowed to access that page.")
                return redirect(dashboard_name_for(request.user))
            return view(request, *args, **kwargs)
        return login_required(wrapper)
    return decorator


def register_view(request):
    if request.user.is_authenticated:
        return redirect(dashboard_name_for(request.user))
    form = RegisterForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            request.session['registered_username'] = user.username
            return redirect('accounts:register_success')
        messages.error(request, "Please fix the errors below.")
    return render(request, 'accounts/register.html', {'form': form})


def register_success(request):
    username = request.session.pop('registered_username', None)
    if not username:
        return redirect('accounts:register')
    return render(request, 'accounts/register_success.html', {'username': username})


class CourtifyLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        from django.urls import reverse
        return reverse(dashboard_name_for(self.request.user))

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password.")
        return super().form_invalid(form)


@login_required
def dashboard_redirect(request):
    return redirect(dashboard_name_for(request.user))


@role_required(User.Role.ADMIN)
def admin_dashboard(request):
    return render(request, 'accounts/admin_dashboard.html')


@role_required(User.Role.CUSTOMER)
def customer_dashboard(request):
    return render(request, 'accounts/customer_dashboard.html')


@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'profile_user': request.user})


@login_required
def profile_edit(request):
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('accounts:profile')
        messages.error(request, "Please fix the errors below.")
    return render(request, 'accounts/profile_edit.html', {'form': form})