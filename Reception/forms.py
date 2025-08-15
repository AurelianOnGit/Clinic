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
        
    def clean_name(self):
        name = self.cleaned_data.get('name')
            
        # Check if the name contains only alphabetic characters and spaces
        if not all(x.isalpha() or x.isspace() for x in name):
            raise forms.ValidationError("Error! A name can only contain Alphabetic characters and spaces")
            
        return name
        
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
            
        if not all(x.isnumeric() for x in phone_number):
            raise forms.ValidationError("Error! A phone number can only contain Numeric characters")
            
        return phone_number
        
class BookTodayForm(BaseAppointmentForm):
    class Meta(BaseAppointmentForm.Meta):
        fields = [
            'name',
            'phone_number',
        ]
        
    def clean_date(self):
        date = timezone.localdate()
        today = timezone.localdate()
            
        if date != today:
            raise forms.ValidationError("You can only book appointments for today!")
            
        return date
        
class BookAnotherDayForm(BaseAppointmentForm):
    class Meta(BaseAppointmentForm.Meta):
        fields = [
            'name',
            'phone_number',
            'date',
        ]
        
    def clean_date(self):
        date = self.cleaned_data['date']
        today = timezone.localdate()   
        
        max_date = today + timezone.timedelta(days=30)
        if date < today or date > max_date:
            raise forms.ValidationError("You can only book within the next 30 days.")
        return date