from django.db import models
from django.utils import timezone

# Create your models here.
class Appointment(models.Model):
    name = models.CharField(max_length=25)
    phone_number = models.CharField(max_length=15)
    date = models.DateField(default=timezone.now)
    token = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('date', 'token')
    
    