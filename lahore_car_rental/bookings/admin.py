from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'vehicle', 'start_date', 'end_date')
    list_filter = ('start_date', 'end_date', 'vehicle__make')
    search_fields = ('user__username', 'vehicle__make',
                     'vehicle__model', 'vehicle__plate')
    date_hierarchy = 'start_date'
    ordering = ['-start_date']
