from rest_framework import serializers
from .models import Car, ErrorCode, CarError

class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = '__all__'

class ErrorCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ErrorCode
        fields = '__all__'

class CarErrorDetailSerializer(serializers.ModelSerializer):
    code = serializers.CharField(source='error_code.obd_code')
    description = serializers.CharField(source='error_code.description')
    severity = serializers.CharField(source='error_code.severity')
    system_category = serializers.CharField(source='error_code.system_category')
    
    class Meta:
        model = CarError
        fields = ['code', 'description', 'severity', 'system_category', 'common_causes', 'solutions']

class CarWithErrorsSerializer(serializers.ModelSerializer):
    errors = serializers.SerializerMethodField()
    
    class Meta:
        model = Car
        fields = ['id', 'brand', 'model', 'year', 'engine_type', 'errors']
    
    def get_errors(self, obj):
        car_errors = CarError.objects.filter(car=obj)
        return CarErrorDetailSerializer(car_errors, many=True).data