from django.contrib import admin
from .models import Vehicle, VehicleImage


class VehicleImageInline(admin.TabularInline):
    model = VehicleImage
    extra = 1


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ("ref", "brand", "model", "year", "vehicle_type", "is_available")
    list_filter = ("vehicle_type", "is_available", "fuel_type", "transmission")
    search_fields = ("ref", "brand", "model")
    inlines = [VehicleImageInline]


@admin.register(VehicleImage)
class VehicleImageAdmin(admin.ModelAdmin):
    list_display = ("id", "vehicle", "image", "order")
    list_filter = ("vehicle",)
