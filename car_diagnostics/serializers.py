from rest_framework import serializers
from .models import CarBrand, Car, ErrorCodeCategory, ErrorCode, CarError, RepairResource

class CarBrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarBrand
        fields = '__all__'

class CarListSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    
    class Meta:
        model = Car
        fields = ['id', 'brand', 'brand_name', 'model', 'year', 'engine_type', 'image']

class CarDetailSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    
    class Meta:
        model = Car
        fields = '__all__'

class ErrorCodeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ErrorCodeCategory
        fields = '__all__'

class ErrorCodeListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = ErrorCode
        fields = ['id', 'obd_code', 'category', 'category_name', 'description', 'severity']

class ErrorCodeDetailSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = ErrorCode
        fields = '__all__'

class RepairResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = RepairResource
        fields = '__all__'

class CarErrorCauseSerializer(serializers.ModelSerializer):
    code = serializers.CharField(source='error_code.obd_code')
    description = serializers.CharField(source='error_code.description')
    severity = serializers.CharField(source='error_code.severity')
    category = serializers.CharField(source='error_code.category.name')
    resources = RepairResourceSerializer(many=True, read_only=True)
    
    class Meta:
        model = CarError
        fields = ['code', 'description', 'severity', 'category', 'common_causes', 
                 'solutions', 'repair_steps', 'estimated_cost', 'resources']

class CarWithErrorsSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    errors = serializers.SerializerMethodField()
    
    class Meta:
        model = Car
        fields = ['id', 'brand', 'brand_name', 'model', 'year', 'engine_type', 'common_issues', 'image', 'errors']
    
    def get_errors(self, obj):
        car_errors = CarError.objects.filter(car=obj)
        return CarErrorCauseSerializer(car_errors, many=True).data