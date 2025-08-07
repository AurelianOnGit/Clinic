from django import forms
from .models import Appointment
from django.utils import timezone

class BaseAppointmentForm(forms.ModelForm):
    class Meta:
        model=Appointment
        fields = [
            'name',
            'phone_number',
            'date',
            'token',
        ]
        
class BookTodayForm(BaseAppointmentForm):
    class Meta(BaseAppointmentForm.Meta):
        fields = {
            'name',
            'phone_number',
        }
        exclude = [
            'date',
            'token',
        ]
        
class BookAnotherDayForm(BaseAppointmentForm):
    class Meta(BaseAppointmentForm.Meta):
        fields = [
            'name',
            'phone_number',
            'date',
        ]
        
    def clean_data(self):
        date = self.cleaned_data['date']
        today = timezone.localdate()   
        
        max_date = today + timezone.timedelta(days=30)
        if date < today or date > max_date:
            raise forms.ValidationError("You can only book within the next 30 days.")
        return date