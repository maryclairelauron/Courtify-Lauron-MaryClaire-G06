
from django import forms
from django.utils import timezone

from courts.models import Court
from .models import Booking


class BookingForm(forms.ModelForm):

    class Meta:
        model = Booking
        fields = [
            'court',
            'booking_date',
            'start_time',
            'end_time',
        ]

        widgets = {
            'court': forms.Select(attrs={
                'class': 'form-control',
            }),
            'booking_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }),
            'start_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
            }),
            'end_time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['court'].queryset = Court.objects.filter(
            status=Court.Status.ACTIVE
        )

    def clean_booking_date(self):
        booking_date = self.cleaned_data['booking_date']

        if booking_date < timezone.localdate():
            raise forms.ValidationError(
                'You cannot book a court for a past date.'
            )

        return booking_date

    def clean(self):
        cleaned_data = super().clean()

        booking_date = cleaned_data.get('booking_date')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time and end_time <= start_time:
            self.add_error(
                'end_time',
                'End time must be later than start time.'
            )

        if (
            booking_date == timezone.localdate()
            and start_time
            and start_time <= timezone.localtime().time()
        ):
            self.add_error(
                'start_time',
                'Please select a future booking time.'
            )

        return cleaned_data
