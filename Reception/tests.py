from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.core.cache import cache
from freezegun import freeze_time
from .models import Appointment

# Create your tests here.
class HomeViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        cache.clear()
        
    def test_home_view_context_variables (self):
        # Make a GET request to the home view
        response = self.client.get(reverse('reception:home'))
        
        # Check the status code
        self.assertEqual(response.status_code, 200)
        
        # Check the context variables for the cache
        self.assertEqual(response.context['ip_book_count'], 0)
        self.assertFalse(response.context['has_booked_today'])
        
    def test_home_view_max_ip_limit(self):
        cache.set(f"booking_limit_127.0.0.1", 5)
        response = self.client.get(reverse('reception:home'))
        
        self.assertEqual(response.context['ip_book_count'], 5)
        self.assertTrue(response.context['has_booked_today'])
        
    def test_five_consecutive_bookings_disables_button(self):
        cache_key = "booking_limit_127.0.0.1"
        for i in range(5):
            current = cache.get(cache_key, 0)
            cache.set(cache_key, current + 1)
            
        response = self.client.get(reverse('reception:home'))
        
        self.assertEqual(response.context['ip_book_count'], 5)  
        self.assertTrue(response.context['has_booked_today'])  
        
class HomeViewTimeTests(TestCase):       
    @freeze_time("2026-04-22 15:00:00 +07:00")
    def test_clinic_is_open_on_wednesday_afternoon(self):
        response = self.client.get(reverse('reception:home'))
        
        self.assertTrue(response.context['is_open'])
        self.assertTrue(response.context['allow_booking'])
        
    @freeze_time("2026-04-26 15:00:00 +07:00")
    def test_clinic_is_open_on_sunday_afternoon(self):
        response = self.client.get(reverse('reception:home'))
        
        self.assertFalse(response.context['is_open'])
        
    @freeze_time("2026-04-27 19:30:00 +07:00")
    def test_clinic_is_open_on_monday_evening(self):
        response = self.client.get(reverse('reception:home'))
        
        self.assertTrue(response.context['is_open'])
        self.assertFalse(response.context['allow_booking'])
        
    @freeze_time("2026-04-27 09:00:00 +07:00")
    def test_next_open_day_is_today_when_not_yet_open(self):
        response = self.client.get(reverse('reception:home'))
        
        # Should be closed at 9AM
        self.assertFalse(response.context['is_open'])
        
        # Next open day should be Monday
        self.assertEqual(response.context['next_open_day'], 'Monday')
        
    @freeze_time("2026-04-27 22:00:00 +07:00")
    def test_for_monday_night(self):
        response = self.client.get(reverse('reception:home'))
        
        self.assertFalse(response.context['is_open'])
        self.assertEqual(response.context['next_open_day'], 'Tuesday')
        self.assertEqual(response.context['days_until_open'], 1)