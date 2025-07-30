from django.contrib import admin
from .models import Vehicle

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'make', 'model', 'year', 'plate')
    search_fields = ('make', 'model', 'plate', 'user__username')
