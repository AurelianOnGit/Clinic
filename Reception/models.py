from django.db import models

# Create your models here.
class Appointment(models.Model):
    name = models.CharField(max_length=25)
    phone_number = models.CharField(max_length=15)
    date = models.DateField()
    token = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name
    