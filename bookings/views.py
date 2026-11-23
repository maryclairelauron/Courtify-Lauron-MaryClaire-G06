
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .models import Booking
from .forms import BookingForm


@login_required
def booking_list(request):
    if request.user.role == 'admin':
        bookings = Booking.objects.select_related(
            'user', 'court'
        ).all()
    else:
        bookings = Booking.objects.filter(
            user=request.user
        ).select_related('court')

    return render(request, 'bookings/booking_list.html', {
        'bookings': bookings,
    })


@login_required
def booking_create(request):
    if request.user.role != 'customer':
        messages.error(request, 'Only customers can create bookings.')
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = BookingForm(request.POST)

        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.status = Booking.Status.PENDING

            try:
                booking.full_clean()
                booking.save()
                messages.success(
                    request,
                    'Your court booking was submitted successfully!'
                )
                return redirect('bookings:booking_list')

            except ValidationError as error:
                if hasattr(error, 'message_dict'):
                    for field, errors in error.message_dict.items():
                        for error_message in errors:
                            form.add_error(field, error_message)
                else:
                    form.add_error(None, error)

    else:
        form = BookingForm()

    return render(request, 'bookings/booking_form.html', {
        'form': form,
        'page_title': 'Book a Court',
    })


@login_required
def booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

    if request.user.role != 'admin' and booking.user != request.user:
        messages.error(request, 'You cannot access this booking.')
        return redirect('bookings:booking_list')

    return render(request, 'bookings/booking_detail.html', {
        'booking': booking,
    })


@login_required
def booking_update(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

    if booking.user != request.user or booking.status == Booking.Status.CANCELLED:
        messages.error(request, 'You cannot edit this booking.')
        return redirect('bookings:booking_list')

    if booking.booking_date < timezone.localdate():
        messages.error(request, 'Past bookings cannot be edited.')
        return redirect('bookings:booking_list')

    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)

        if form.is_valid():
            updated_booking = form.save(commit=False)

            try:
                updated_booking.full_clean()
                updated_booking.save()
                messages.success(request, 'Booking updated successfully!')
                return redirect('bookings:booking_list')

            except ValidationError as error:
                if hasattr(error, 'message_dict'):
                    for field, errors in error.message_dict.items():
                        for error_message in errors:
                            form.add_error(field, error_message)
                else:
                    form.add_error(None, error)

    else:
        form = BookingForm(instance=booking)

    return render(request, 'bookings/booking_form.html', {
        'form': form,
        'page_title': 'Update Booking',
    })


@login_required
def booking_cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk)

    if request.method != 'POST':
        return redirect('bookings:booking_list')

    if request.user.role != 'admin' and booking.user != request.user:
        messages.error(request, 'You cannot cancel this booking.')
        return redirect('bookings:booking_list')

    if booking.status == Booking.Status.CANCELLED:
        messages.warning(request, 'This booking is already cancelled.')
    else:
        booking.status = Booking.Status.CANCELLED
        booking.save(update_fields=['status'])
        messages.success(request, 'Booking cancelled successfully!')

    return redirect('bookings:booking_list')
