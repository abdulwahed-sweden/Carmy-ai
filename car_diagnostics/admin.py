from django.contrib import admin
from .models import (
    CarBrand, Car, ErrorCodeCategory, ErrorCode, CarError, RepairResource
)

@admin.register(CarBrand)
class CarBrandAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('brand', 'model', 'year', 'engine_type')
    list_filter = ('brand', 'year')
    search_fields = ('model', 'brand__name')

@admin.register(ErrorCodeCategory)
class ErrorCodeCategoryAdmin(admin.ModelAdmin):
    list_display = ('code_prefix', 'name', 'category_type')
    list_filter = ('category_type',)
    search_fields = ('name', 'code_prefix')

@admin.register(ErrorCode)
class ErrorCodeAdmin(admin.ModelAdmin):
    list_display = ('obd_code', 'category', 'description', 'severity')
    list_filter = ('category', 'severity', 'repair_difficulty')
    search_fields = ('obd_code', 'description')

class RepairResourceInline(admin.TabularInline):
    model = RepairResource
    extra = 1

@admin.register(CarError)
class CarErrorAdmin(admin.ModelAdmin):
    list_display = ('car', 'error_code')
    list_filter = ('car__brand', 'error_code__category')
    search_fields = ('car__model', 'error_code__obd_code', 'common_causes')
    inlines = [RepairResourceInline]

@admin.register(RepairResource)
class RepairResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'car_error', 'resource_type')
    list_filter = ('resource_type',)
    search_fields = ('title', 'car_error__car__model', 'car_error__error_code__obd_code')