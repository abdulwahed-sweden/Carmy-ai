from django.shortcuts import render
from django.db.models import Q

from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Car, ErrorCode, CarError
from .serializers import (
    CarSerializer, 
    ErrorCodeSerializer, 
    CarWithErrorsSerializer
)

class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['brand', 'model', 'year']
    search_fields = ['brand', 'model']
    
    @action(detail=True, methods=['get'])
    def errors(self, request, pk=None):
        car = self.get_object()
        serializer = CarWithErrorsSerializer(car)
        return Response(serializer.data)

class ErrorCodeViewSet(viewsets.ModelViewSet):
    queryset = ErrorCode.objects.all()
    serializer_class = ErrorCodeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['obd_code', 'severity', 'system_category']
    search_fields = ['obd_code', 'description']
    
    @action(detail=True, methods=['get'])
    def affected_cars(self, request, pk=None):
        error_code = self.get_object()
        cars = Car.objects.filter(car_errors__error_code=error_code)
        serializer = CarSerializer(cars, many=True)
        return Response(serializer.data)
    



def search_results(request):
    brand = request.GET.get('brand', '')
    model = request.GET.get('model', '')
    year = request.GET.get('year', '')
    obd_code = request.GET.get('obd_code', '')
    
    results = None
    
    # البحث عن كود عطل محدد
    if obd_code:
        error_codes = ErrorCode.objects.filter(obd_code__icontains=obd_code)
        if error_codes.exists():
            results = {
                'type': 'error_code',
                'data': error_codes
            }
    
    # البحث عن سيارة محددة
    elif any([brand, model, year]):
        query = Q()
        if brand:
            query &= Q(brand=brand)
        if model:
            query &= Q(model__icontains=model)
        if year:
            query &= Q(year=year)
        
        cars = Car.objects.filter(query)
        if cars.exists():
            results = {
                'type': 'car',
                'data': cars
            }
    
    return render(request, 'car_diagnostics/search_results.html', {
        'results': results,
        'search_params': {
            'brand': brand,
            'model': model,
            'year': year,
            'obd_code': obd_code
        }
    })