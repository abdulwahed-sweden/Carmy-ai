from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.shortcuts import render, get_object_or_404

from .models import CarBrand, Car, ErrorCodeCategory, ErrorCode, CarError, RepairResource
from .serializers import (
    CarBrandSerializer, CarListSerializer, CarDetailSerializer,
    ErrorCodeCategorySerializer, ErrorCodeListSerializer, ErrorCodeDetailSerializer,
    CarWithErrorsSerializer, RepairResourceSerializer, CarErrorCauseSerializer
)

# Frontend views
def index(request):
    """View for the main car diagnostics page"""
    return render(request, 'car_diagnostics/index.html')

def car_search(request):
    """View for searching cars"""
    brands = CarBrand.objects.all()
    return render(request, 'car_diagnostics/car_search.html', {'brands': brands})

def error_search(request):
    """View for searching error codes"""
    categories = ErrorCodeCategory.objects.all()
    return render(request, 'car_diagnostics/error_search.html', {'categories': categories})

def smart_diagnostic(request):
    """View for the smart diagnostic page"""
    brands = CarBrand.objects.all()
    return render(request, 'car_diagnostics/smart_diagnostic.html', {'brands': brands})

def obd_scanner(request):
    """View for the OBD scanner page"""
    return render(request, 'car_diagnostics/obd_scanner.html')

# API views
class CarBrandViewSet(viewsets.ModelViewSet):
    queryset = CarBrand.objects.all()
    serializer_class = CarBrandSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

    @action(detail=True, methods=['get'])
    def models(self, request, pk=None):
        brand = self.get_object()
        cars = Car.objects.filter(brand=brand)
        serializer = CarListSerializer(cars, many=True)
        return Response(serializer.data)


class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['brand', 'model', 'year']
    search_fields = ['brand__name', 'model']

    def get_serializer_class(self):
        if self.action == 'list':
            return CarListSerializer
        elif self.action in ['retrieve', 'errors']:
            return CarWithErrorsSerializer
        return CarDetailSerializer

    @action(detail=True, methods=['get'])
    def errors(self, request, pk=None):
        car = self.get_object()
        serializer = CarWithErrorsSerializer(car)
        return Response(serializer.data)


class ErrorCodeCategoryViewSet(viewsets.ModelViewSet):
    queryset = ErrorCodeCategory.objects.all()
    serializer_class = ErrorCodeCategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'code_prefix']


class ErrorCodeViewSet(viewsets.ModelViewSet):
    queryset = ErrorCode.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['obd_code', 'severity', 'category']
    search_fields = ['obd_code', 'description']

    def get_serializer_class(self):
        if self.action == 'list':
            return ErrorCodeListSerializer
        return ErrorCodeDetailSerializer

    @action(detail=True, methods=['get'])
    def affected_cars(self, request, pk=None):
        error_code = self.get_object()
        cars = Car.objects.filter(car_errors__error_code=error_code)
        serializer = CarListSerializer(cars, many=True)
        return Response(serializer.data)


class DiagnosticSearchViewSet(viewsets.ViewSet):
    """واجهة برمجية للبحث الذكي عن الأعطال"""

    def list(self, request):
        brand = request.query_params.get('brand')
        model = request.query_params.get('model')
        year = request.query_params.get('year')
        obd_code = request.query_params.get('obd_code')

        if obd_code:
            try:
                error_code = ErrorCode.objects.get(obd_code=obd_code)

                car = None
                if brand and model and year:
                    try:
                        brand_obj = CarBrand.objects.get(name=brand)
                        car = Car.objects.get(brand=brand_obj, model=model, year=year)
                        car_error = CarError.objects.get(car=car, error_code=error_code)
                        serializer = CarWithErrorsSerializer(car)
                        return Response(serializer.data)
                    except (CarBrand.DoesNotExist, Car.DoesNotExist, CarError.DoesNotExist):
                        response_data = {
                            'code': error_code.obd_code,
                            'description': error_code.description,
                            'severity': error_code.severity,
                            'category': error_code.category.name,
                            'emergency_action': error_code.emergency_action,
                            'repair_difficulty': error_code.repair_difficulty,
                            'message': 'لم يتم العثور على معلومات محددة لهذه السيارة. هذه معلومات عامة عن كود العطل.'
                        }
                        return Response(response_data)
                
                response_data = {
                    'code': error_code.obd_code,
                    'description': error_code.description,
                    'severity': error_code.severity,
                    'category': error_code.category.name,
                    'emergency_action': error_code.emergency_action,
                    'repair_difficulty': error_code.repair_difficulty,
                    'affected_cars': CarListSerializer(
                        Car.objects.filter(car_errors__error_code=error_code), many=True
                    ).data
                }
                return Response(response_data)

            except ErrorCode.DoesNotExist:
                return Response({'message': 'كود العطل غير موجود'}, status=status.HTTP_404_NOT_FOUND)

        elif brand or model or year:
            query = Q()
            if brand:
                try:
                    brand_obj = CarBrand.objects.get(name=brand)
                    query &= Q(brand=brand_obj)
                except CarBrand.DoesNotExist:
                    return Response({'message': 'الشركة المصنعة غير موجودة'}, status=status.HTTP_404_NOT_FOUND)
            if model:
                query &= Q(model__icontains=model)
            if year:
                query &= Q(year=year)

            cars = Car.objects.filter(query)
            if cars.exists():
                serializer = CarListSerializer(cars, many=True)
                return Response(serializer.data)
            else:
                return Response({'message': 'لم يتم العثور على سيارات مطابقة'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'message': 'يرجى تحديد معايير البحث'}, status=status.HTTP_400_BAD_REQUEST)


class SmartDiagnosticAPIView(APIView):
    """واجهة برمجية للتشخيص الذكي للأعطال بناءً على وصف المشكلة"""

    def post(self, request):
        car_brand = request.data.get('brand')
        car_model = request.data.get('model')
        car_year = request.data.get('year')
        problem_description = request.data.get('problem_description')

        if not problem_description:
            return Response(
                {'error': 'يرجى تقديم وصف للمشكلة'},
                status=status.HTTP_400_BAD_REQUEST
            )

        car = None
        if car_brand and car_model and car_year:
            try:
                brand = CarBrand.objects.get(name=car_brand)
                car = Car.objects.get(brand=brand, model=car_model, year=car_year)
            except (CarBrand.DoesNotExist, Car.DoesNotExist):
                pass

        # Dictionary mapping symptoms to potential error codes
        symptoms_to_codes = {
            'misfire': ['P0300', 'P0301', 'P0302', 'P0303', 'P0304'],
            'shaking': ['P0300', 'P0301', 'P0302', 'P0303', 'P0304'],
            'vibration': ['P0300', 'P0301', 'P0302', 'P0303', 'P0304'],
            'hesitation': ['P0171', 'P0174', 'P0101', 'P0102'],
            'poor fuel': ['P0171', 'P0174', 'P0101', 'P0102'],
            'weak acceleration': ['P0171', 'P0174', 'P0101', 'P0102'],
            'overheat': ['P0115', 'P0116', 'P0117', 'P0118', 'P0125'],
            'overheating': ['P0115', 'P0116', 'P0117', 'P0118', 'P0125'],
            'temperature': ['P0115', 'P0116', 'P0117', 'P0118', 'P0125'],
            'emission': ['P0420', 'P0430', 'P0440', 'P0442', 'P0446'],
            'emissions': ['P0420', 'P0430', 'P0440', 'P0442', 'P0446'],
            'check engine': ['P0120', 'P0121', 'P0122', 'P0123', 'P0700'],
            'light': ['P0120', 'P0121', 'P0122', 'P0123', 'P0700'],
            'transmission': ['P0700', 'P0701', 'P0702', 'P0705', 'P0706'],
            'gear': ['P0700', 'P0701', 'P0702', 'P0705', 'P0706'],
            'shifting': ['P0700', 'P0701', 'P0702', 'P0705', 'P0706'],
            'rough idle': ['P0505', 'P0506', 'P0507', 'P0300'],
            'idle': ['P0505', 'P0506', 'P0507', 'P0300'],
            'stall': ['P0505', 'P0506', 'P0507', 'P0300'],
        }

        # Identify potential error codes based on keywords in the problem description
        possible_codes = set()
        keywords = problem_description.lower().split()
        for keyword in keywords:
            for symptom, codes in symptoms_to_codes.items():
                if keyword in symptom or symptom in keyword:
                    possible_codes.update(codes)

        error_codes = ErrorCode.objects.filter(obd_code__in=possible_codes)

        # If a car is identified, find car-specific errors
        car_specific_errors = []
        if car and error_codes:
            car_errors = CarError.objects.filter(car=car, error_code__in=error_codes)
            if car_errors.exists():
                car_specific_errors = [
                    {
                        'code': error.error_code.obd_code,
                        'description': error.error_code.description,
                        'severity': error.error_code.severity,
                        'common_causes': error.common_causes,
                        'solutions': error.solutions,
                        'estimated_cost': error.estimated_cost
                    }
                    for error in car_errors
                ]

        response_data = {
            'query': problem_description,
            'possible_codes': [
                {
                    'code': code.obd_code,
                    'description': code.description,
                    'severity': code.severity,
                    'category': code.category.name
                }
                for code in error_codes
            ]
        }

        if car:
            response_data['car'] = {
                'brand': car.brand.name,
                'model': car.model,
                'year': car.year
            }
            response_data['car_specific_errors'] = car_specific_errors

        return Response(response_data)


class OBDSimulatorAPIView(APIView):
    """واجهة برمجية لمحاكاة قراءة أكواد OBD-II لأغراض الاختبار"""
    
    def post(self, request):
        import random
        
        car_id = request.data.get('car_id')
        simulate_type = request.data.get('simulate_type', 'random')
        
        if not car_id:
            return Response({'error': 'يجب توفير معرف السيارة'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            car = Car.objects.get(id=car_id)
        except Car.DoesNotExist:
            return Response({'error': 'السيارة المحددة غير موجودة'}, status=status.HTTP_404_NOT_FOUND)
        
        # Common OBD-II codes for simulation
        common_codes = [
            'P0300', 'P0301', 'P0302', 'P0303', 'P0171', 'P0174',
            'P0420', 'P0430', 'P0440', 'P0442', 'P0446',
            'P0455', 'P0456', 'P0700', 'P0128'
        ]
        
        # Codes based on simulation type
        if simulate_type == 'engine_misfire':
            codes = ['P0300', 'P0301', 'P0302']
        elif simulate_type == 'fuel_system':
            codes = ['P0171', 'P0174', 'P0172']
        elif simulate_type == 'emissions':
            codes = ['P0420', 'P0430', 'P0440']
        elif simulate_type == 'transmission':
            codes = ['P0700', 'P0730', 'P0740']
        elif simulate_type == 'random_critical':
            # Simulate critical random issues
            critical_codes = ['P0300', 'P0303', 'P0116', 'P0217', 'P0505']
            codes = random.sample(critical_codes, k=random.choice([1, 2]))
        else:  # random
            # Select a random number of codes
            num_codes = random.choice([1, 2, 3])
            codes = random.sample(common_codes, k=num_codes)
        
        # Add some unknown codes that may not be in the database
        unknown_codes = [f'P{random.randint(1000, 9999)}' for _ in range(random.choice([0, 1]))]
        
        # Combine known and unknown codes
        all_codes = codes + unknown_codes
        
        return Response({
            'car': {
                'id': car.id,
                'brand': car.brand.name,
                'model': car.model,
                'year': car.year
            },
            'obd_codes': all_codes,
            'note': 'هذه بيانات محاكاة لأغراض الاختبار فقط.'
        })


class OBDDeviceDataAPIView(APIView):
    """واجهة برمجية لمعالجة البيانات الواردة من جهاز OBD-II"""
    
    def post(self, request):
        car_id = request.data.get('car_id')
        obd_codes = request.data.get('obd_codes', [])
        
        if not car_id or not obd_codes:
            return Response(
                {'error': 'يجب توفير معرف السيارة وأكواد OBD-II'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            car = Car.objects.get(id=car_id)
        except Car.DoesNotExist:
            return Response(
                {'error': 'السيارة المحددة غير موجودة'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Find the error codes in the database
        error_codes = ErrorCode.objects.filter(obd_code__in=obd_codes)
        
        # Prepare diagnostics results
        diagnostics = []
        for error_code in error_codes:
            try:
                car_error = CarError.objects.get(car=car, error_code=error_code)
                resources = RepairResourceSerializer(car_error.resources.all(), many=True).data
                
                diagnostic = {
                    'code': error_code.obd_code,
                    'description': error_code.description,
                    'severity': error_code.severity,
                    'category': error_code.category.name,
                    'common_causes': car_error.common_causes,
                    'solutions': car_error.solutions,
                    'repair_steps': car_error.repair_steps,
                    'estimated_cost': car_error.estimated_cost,
                    'emergency_action': error_code.emergency_action,
                    'resources': resources
                }
            except CarError.DoesNotExist:
                # If no car-specific info exists, return general error code info
                diagnostic = {
                    'code': error_code.obd_code,
                    'description': error_code.description,
                    'severity': error_code.severity,
                    'category': error_code.category.name,
                    'emergency_action': error_code.emergency_action,
                    'note': 'لا تتوفر معلومات محددة لهذا العطل في سيارتك. هذه معلومات عامة.'
                }
            
            diagnostics.append(diagnostic)
        
        # Identify codes that weren't found in the database
        missing_codes = set(obd_codes) - set(error_codes.values_list('obd_code', flat=True))
        
        return Response({
            'car': {
                'id': car.id,
                'brand': car.brand.name,
                'model': car.model,
                'year': car.year,
                'engine_type': car.engine_type
            },
            'diagnostics': diagnostics,
            'missing_codes': list(missing_codes)
        })