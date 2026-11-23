
from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.utils import timezone

from .forms import RegisterForm, ProfileForm
from .models import User
from bookings.models import Booking
from courts.models import Court

from django.contrib.auth import logout
from django.views.decorators.http import require_POST


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
                messages.error(
                    request,
                    "You are not allowed to access that page."
                )
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

    return render(
        request,
        'accounts/register_success.html',
        {'username': username}
    )


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
    today = timezone.localdate()

    context = {
        'today': today,
        'total_bookings': Booking.objects.count(),
        'today_bookings': Booking.objects.filter(
            booking_date=today
        ).count(),
        'pending_bookings': Booking.objects.filter(
            status=Booking.Status.PENDING
        ).count(),
        'confirmed_bookings': Booking.objects.filter(
            status=Booking.Status.CONFIRMED
        ).count(),
        'active_courts': Court.objects.filter(
            status=Court.Status.ACTIVE
        ).count(),
        'maintenance_courts': Court.objects.filter(
            status=Court.Status.MAINTENANCE
        ).count(),
        'recent_bookings': Booking.objects.select_related(
            'user', 'court'
        ).order_by('-created_at')[:6],
    }

    return render(
        request,
        'accounts/admin_dashboard.html',
        context
    )


@role_required(User.Role.CUSTOMER)
def customer_dashboard(request):
    today = timezone.localdate()

    customer_bookings = Booking.objects.filter(user=request.user)

    upcoming_bookings = customer_bookings.filter(
        booking_date__gte=today,
        status__in=[
            Booking.Status.PENDING,
            Booking.Status.CONFIRMED,
        ]
    ).select_related('court').order_by(
        'booking_date', 'start_time'
    )

    context = {
        'today': today,
        'total_bookings': customer_bookings.count(),
        'upcoming_count': upcoming_bookings.count(),
        'pending_count': customer_bookings.filter(
            status=Booking.Status.PENDING
        ).count(),
        'upcoming_bookings': upcoming_bookings[:5],
    }

    return render(
        request,
        'accounts/customer_dashboard.html',
        context
    )


@login_required
def profile_view(request):
    form = ProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user
    )

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('accounts:profile')

        messages.error(request, "Please fix the errors below.")

    return render(
        request,
        'accounts/profile.html',
        {
            'profile_user': request.user,
            'form': form,
        }
    )


@login_required
def profile_edit(request):
    form = ProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user
    )

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('accounts:profile')

        messages.error(request, "Please fix the errors below.")

    return render(
        request,
        'accounts/profile_edit.html',
        {'form': form}
    )

@login_required
@require_POST
def delete_account(request):
    if request.user.role == User.Role.ADMIN:
        messages.error(
            request,
            "Admin accounts cannot be deleted here."
        )
        return redirect('accounts:profile')

    user = request.user

    logout(request)
    user.delete()

    messages.success(request, "Your account has been deleted.")

    return redirect('accounts:login')
