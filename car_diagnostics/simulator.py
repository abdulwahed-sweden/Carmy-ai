# simulator.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from random import sample, choice

@method_decorator(csrf_exempt, name='dispatch')
class OBDSimulatorAPIView(APIView):
    """واجهة برمجية لمحاكاة قراءة أكواد OBD-II لأغراض الاختبار"""
    
    def post(self, request):
        car_id = request.data.get('car_id')
        simulate_type = request.data.get('simulate_type', 'random')
        
        if not car_id:
            return Response({'error': 'يجب توفير معرف السيارة'}, status=400)
        
        try:
            car = Car.objects.get(id=car_id)
        except Car.DoesNotExist:
            return Response({'error': 'السيارة المحددة غير موجودة'}, status=404)
        
        # أكواد OBD-II الشائعة للمحاكاة
        common_codes = [
            'P0300', 'P0301', 'P0302', 'P0303', 'P0171', 'P0174',
            'P0420', 'P0430', 'P0440', 'P0442', 'P0446',
            'P0455', 'P0456', 'P0700', 'P0128'
        ]
        
        # أكواد حسب نوع المحاكاة
        if simulate_type == 'engine_misfire':
            codes = ['P0300', 'P0301', 'P0302']
        elif simulate_type == 'fuel_system':
            codes = ['P0171', 'P0174', 'P0172']
        elif simulate_type == 'emissions':
            codes = ['P0420', 'P0430', 'P0440']
        elif simulate_type == 'transmission':
            codes = ['P0700', 'P0730', 'P0740']
        elif simulate_type == 'random_critical':
            # محاكاة أعطال حرجة عشوائية
            critical_codes = ['P0300', 'P0303', 'P0116', 'P0217', 'P0505']
            codes = sample(critical_codes, k=choice([1, 2]))
        else:  # random
            # اختيار عدد عشوائي من الأكواد
            num_codes = choice([1, 2, 3])
            codes = sample(common_codes, k=num_codes)
        
        # اختيار بعض الأكواد غير الموجودة في قاعدة البيانات
        unknown_codes = [f'P{choice(range(1000, 10000))}' for _ in range(choice([0, 1]))]
        
        # إضافة الأكواد المعروفة وغير المعروفة
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