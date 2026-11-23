from django import forms

from .models import Court


class CourtForm(forms.ModelForm):
    class Meta:
        model = Court
        fields = ('name', 'environment', 'rate_per_hour', 'max_players', 'status', 'description')
        labels = {
                    'rate_per_hour': 'Rate per hour (PHP)',
                    'max_players': 'Max players',
        }
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Court 1'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if Court.objects.filter(name__iexact=name).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("A court with this name already exists.")
        return name