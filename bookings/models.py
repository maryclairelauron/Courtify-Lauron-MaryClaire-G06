
from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from courts.models import Court


class Booking(models.Model):

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        CANCELLED = 'cancelled', 'Cancelled'

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookings'
    )

    court = models.ForeignKey(
        Court,
        on_delete=models.PROTECT,
        related_name='bookings'
    )

    booking_date = models.DateField()

    start_time = models.TimeField()

    end_time = models.TimeField()

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )

    status = models.CharField(
        max_length=12,
        choices=Status.choices,
        default=Status.PENDING
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-booking_date', '-start_time']

    def clean(self):
        super().clean()

        errors = {}

        if self.booking_date:
            if self.booking_date < timezone.localdate():
                errors['booking_date'] = (
                    'You cannot book a court for a past date.'
                )

            elif (
                self.booking_date == timezone.localdate()
                and self.start_time
                and self.start_time <= timezone.localtime().time()
            ):
                errors['start_time'] = (
                    'The booking time must be in the future.'
                )

        if self.start_time and self.end_time:
            if self.end_time <= self.start_time:
                errors['end_time'] = (
                    'End time must be later than start time.'
                )

        if self.court_id and self.booking_date:
            if self.court.status != Court.Status.ACTIVE:
                errors['court'] = (
                    'This court is currently under maintenance.'
                )

        if (
            self.court_id
            and self.booking_date
            and self.start_time
            and self.end_time
            and self.end_time > self.start_time
            and self.status != self.Status.CANCELLED
        ):
            overlapping = Booking.objects.filter(
                court_id=self.court_id,
                booking_date=self.booking_date,
                start_time__lt=self.end_time,
                end_time__gt=self.start_time
            ).exclude(
                status=self.Status.CANCELLED
            )

            if self.pk:
                overlapping = overlapping.exclude(pk=self.pk)

            if overlapping.exists():
                errors['start_time'] = (
                    'This court is already booked during that time.'
                )

        if errors:
            raise ValidationError(errors)

        if (
            self.court_id
            and self.start_time
            and self.end_time
            and self.end_time > self.start_time
        ):
            start_minutes = (
                self.start_time.hour * 60 + self.start_time.minute
            )

            end_minutes = (
                self.end_time.hour * 60 + self.end_time.minute
            )

            duration = Decimal(end_minutes - start_minutes) / Decimal(60)

            self.total_price = (
                self.court.rate_per_hour * duration
            ).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def __str__(self):
        return (
            f'{self.user.username} - {self.court.name} '
            f'({self.booking_date})'
        )
