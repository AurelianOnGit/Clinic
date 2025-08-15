from django.shortcuts import render, redirect, reverse
from .models import Appointment
from django.utils import timezone
from .forms import BookTodayForm, BookAnotherDayForm
from django.db.models import Max
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator

# Create your views here.
def home(request):
    appointments = Appointment.objects.all().order_by('token')
    paginator = Paginator(appointments, 25) # 25 per page
    
    page_number = request.GET.get('page') # which page are we on
    page_obj = paginator.get_page(page_number) # gives page data and nav helpers
    
    today = timezone.localdate()
    today_weekday = today.weekday()
    closed_days = [5, 6]
    is_open = today_weekday not in closed_days
    
    for i in range (1, 8):
        next_day = (today_weekday + i) % 7
        
        if next_day not in closed_days:
            next_open_day_index = next_day
            break
    
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    next_open_day_name = weekdays[next_open_day_index]
    
    appointments_today = Appointment.objects.filter(date=today).order_by("token")
    context = {
        "appointments" : appointments_today,
        "is_open" : is_open,
        "next_open_day" : next_open_day_name,
        'page_obj' : page_obj,
    }
    
    return render(request, "Reception/home.html", context)

def book_today(request):
    success = 'success' in request.GET
    if request.method == 'POST':
        form = BookTodayForm(request.POST)
        
        if form.is_valid():
            booking = form.save(commit=False)
            booking.date = timezone.now().date()
            
            # filters all appointment entries with the same date as booking, then calculates the max
            # value of the token field among those filtered objects. THe result is put inside a dictionary
            max_token = Appointment.objects.filter(date=booking.date).aggregate(Max('token'))['token__max']
            
            next_token = 1 if max_token is None else max_token + 1
            
            if next_token > 100:
                form.add_error(None, "All 100 booking slots for today have been filled.")
            else:
                booking.token = next_token
                booking.save()
                
                success_url = f"{reverse('reception:book_today')}?success=true"
                return redirect(success_url)     
    else:
        form = BookTodayForm()
        
    return render(request, 'Reception/book_today.html', {'form' : form, 'success' : success})
    
def book_another_day(request):
    if request.method == 'POST':
        form = BookAnotherDayForm(request.POST)
        
        if form.is_valid():
            booking = form.save(commit=False)
            
            max_token = Appointment.objects.filter(date=booking.date).aggregate(Max('token'))['token']
            
            next_token = 1 if max_token is None else max_token + 1
            
            if next_token > 100:
                form.add_error(None, "All 100 booking slots for today have been filled.")
            else:
                booking.token = next_token
                booking.save()
                success =True
            
            
    else:
        form = BookAnotherDayForm(request.POST)
        
    return render(request, 'book_another_day.html', {'form' : form, 'success' : success})
            
            