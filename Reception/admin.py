from django.contrib import admin
from .models import Appointment

# Register your models here.
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'token', 'created_at')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
    
admin.site.register(Appointment, AppointmentAdmin)