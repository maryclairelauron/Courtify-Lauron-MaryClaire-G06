
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'username',
            'email',
            'contact_number',
            'password1',
            'password2',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['contact_number'].widget.attrs['placeholder'] = '0917 123 4567'
        self.fields['password1'].widget.attrs['placeholder'] = 'At least 8 characters'
        self.fields['password2'].widget.attrs['placeholder'] = 'Re-enter your password'

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "This email is already registered."
            )

        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.CUSTOMER

        if commit:
            user.save()

        return user


class ProfileForm(forms.ModelForm):
    full_name = forms.CharField(
        max_length=150,
        required=True,
        label='Full name'
    )

    class Meta:
        model = User
        fields = ('email', 'contact_number', 'profile_photo')
        labels = {
            'contact_number': 'Phone number',
            'profile_photo': 'Profile photo',
        }
        widgets = {
            'profile_photo': forms.FileInput(),
        }

    field_order = [
        'full_name',
        'email',
        'contact_number',
        'profile_photo',
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['full_name'] = self.instance.get_full_name()

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()

        if User.objects.filter(
            email__iexact=email
        ).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError(
                "This email is already in use."
            )

        return email

    def save(self, commit=True):
        user = super().save(commit=False)

        parts = self.cleaned_data['full_name'].strip().split(None, 1)

        user.first_name = parts[0]
        user.last_name = parts[1] if len(parts) > 1 else ''

        if commit:
            user.save()

        return user
