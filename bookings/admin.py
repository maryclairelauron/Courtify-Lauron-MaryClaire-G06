
from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'user',
        'court',
        'booking_date',
        'start_time',
        'end_time',
        'total_price',
        'status',
    )

    list_filter = (
        'status',
        'booking_date',
        'court',
    )

    search_fields = (
        'user__username',
        'court__name',
    )

    ordering = ('-booking_date', '-start_time')
