from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from .models import Review, Order, Booking


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=False, label='Email')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class StyledAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']
        widgets = {
            'rating': forms.Select(choices=[(i, f'{i} ★') for i in range(1, 6)], attrs={'class': 'form-select'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Поділись враженням про страву...'}),
        }


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['name', 'phone', 'address', 'payment_method']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ім\u2019я та прізвище'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+380...'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Вулиця, будинок, квартира'}),
            'payment_method': forms.RadioSelect,
        }


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['name', 'phone', 'date', 'time', 'guests']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ім\u2019я'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+380...'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'guests': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

    def __init__(self, *args, table=None, **kwargs):
        self.table = table
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned = super().clean()
        guests = cleaned.get('guests')
        if self.table and guests and guests > self.table.seats:
            self.add_error('guests', f'У цього столика максимум {self.table.seats} місць.')
        date, time = cleaned.get('date'), cleaned.get('time')
        if self.table and date and time:
            if self.table.bookings.filter(date=date, time=time).exists():
                raise forms.ValidationError('Цей столик уже заброньовано на обрані дату й час. Обери інший час або столик.')
        return cleaned
