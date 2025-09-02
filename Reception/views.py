from django.shortcuts import render, redirect, reverse
from .models import Appointment
from django.utils import timezone
from .forms import BookTodayForm, BookAnotherDayForm
from django.db.models import Max, Q
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from datetime import timedelta, time

# Create your views here.
def home(request):    
    today_aware = timezone.localtime()
    today_date = today_aware.date()
    today_weekday = today_date.weekday()
    closed_days = [5]
    
    # Clinic open and close times
    opening_time = time(hour= 15, minute= 0)
    closing_time = time(hour= 20, minute= 0)
    current_time = today_aware.time()
    
    is_open = (today_weekday not in closed_days) and (opening_time <= current_time < closing_time)
    
    appointments = Appointment.objects.filter(date=today_date).order_by('token')
    paginator = Paginator(appointments, 20) # 20 per page
    
    page_number = request.GET.get('page') # which page are we on
    page_obj = paginator.get_page(page_number) # gives page data and nav helpers
    
    for i in range (1, 8):
        next_day = (today_weekday + i) % 7
        
        if next_day not in closed_days:
            next_open_day_index = next_day
            break
    
    # Calculate the date of the next open day    
    days_until_open = (next_open_day_index - today_weekday + 7) % 7
    if days_until_open == 0 and not is_open:
        days_until_open = 7
        
    next_open_day_aware = today_aware.replace(
        hour= 0,
        minute= 0,
        second= 0,
        microsecond= 0
    ) + timedelta(days=days_until_open)
    
    # Combine both the date and time to make a full datetime object
    next_open_datetime =  next_open_day_aware.replace(hour=8, minute=0)
    
    # --- FOR TESTING ONLY ---
    # Set the next open datetime to a few seconds in the future
    #next_open_datetime = timezone.localtime() + timedelta(seconds=10)
    # --- END OF TESTING CODE ---
    
    # Calculate time until closing for the "book today" button
    closing_datetime = today_aware.replace(hour= 20, minute= 0, second= 0, microsecond= 0)
    
    # This will be True if it's more than 1 hour until closing
    time_to_close = closing_datetime - today_aware
    allow_booking = time_to_close > timedelta(hours= 1)
    
    # Check for session flag from the book_today view
    has_book_today = request.session.get('has_booked_today', False)
    if has_book_today:
        del request.session['has_booked_today'] # Clear the flag for future visits
    
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    next_open_day_name = weekdays[next_open_day_index]
    
    appointments_today = Appointment.objects.filter(date=today_date).order_by("token")
    context = {
        "appointments" : appointments_today,
        "is_open" : is_open,
        "next_open_day" : next_open_day_name,
        "page_obj" : page_obj,
        "next_open_datetime" : next_open_datetime.isoformat(),
        "closing_datetime" : closing_datetime.isoformat(),
        "allow_booking" : allow_booking,
        "has_booked_today" : has_book_today,        
    }
    
    return render(request, "Reception/home.html", context)

def book_today(request):
    success = 'success' in request.GET
    if request.method == 'POST':
        form = BookTodayForm(request.POST)
        
        if form.is_valid():
            # Server-side validation for duplicate bookings
            name = form.cleaned_data['name']
            phone_number  = form.cleaned_data['phone_number']
            today_date = timezone.localdate()
            
            existing_appointments = Appointment.objects.filter(
                (Q(name=name) | Q(phone_number=phone_number)),
                date=today_date
            ).exists()
            
            if existing_appointments:
                form.add_error(None, "An appointment for this name or phone number already exists for today<br>If your details are wrong, please contact this number: 0967979104")
                return render(request, 'Reception/book_today.html', {'form': form, 'success': success})
            
            booking = form.save(commit=False)
            booking.date = timezone.now().date()
            
            # Filters all appointment entries with the same date as booking, then calculates the max
            # value of the token field among those filtered objects. The result is put inside a dictionary.
            max_token = Appointment.objects.filter(date=booking.date).aggregate(Max('token'))['token__max']
            
            next_token = 1 if max_token is None else max_token + 1
            
            if next_token > 100:
                form.add_error(None, "All 100 booking slots for today have been filled.")
            else:
                booking.token = next_token
                booking.save()
                
                # Set a session flag on successful booking
                request.session['has_booked_today'] = True
                
                success_url = f"{reverse('reception:book_today')}?success=true"
                return redirect(success_url)     
    else:
        form = BookTodayForm()
        
    return render(request, 'Reception/book_today.html', {'form' : form, 'success' : success})
    
def book_another_day(request):
    success = 'success' in request.GET
    if request.method == 'POST':
        form = BookAnotherDayForm(request.POST)
        
        if form.is_valid():
            booking = form.save(commit=False)
            
            max_token = Appointment.objects.filter(date=booking.date).aggregate(Max('token'))['token__max']
            
            next_token = 1 if max_token is None else max_token + 1
            
            if next_token > 100:
                form.add_error(None, "All 100 booking slots for today have been filled.")
            else:
                booking.token = next_token
                booking.save()
                success =True
                
                success_url = f"{reverse('reception:book_later')}?success=true"
                return redirect(success_url)                   
    else:
        form = BookAnotherDayForm()
        
    return render(request, 'Reception/book_later.html', {'form' : form, 'success' : success})
            
            