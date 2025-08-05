from django.shortcuts import render
from .models import Appointment
from django.utils import timezone

# Create your views here.
def home(request):
    today = timezone.localdate()
    appointments_today = Appointment.objects.filter(date=today).order_by("token")
    context = {
        "appointments" : appointments_today
    }
    
    return render(request, "Reception\home.html", context)