import csv
import re
from django.core.management.base import BaseCommand
from car_diagnostics.models import ErrorCodeCategory, ErrorCode

class Command(BaseCommand):
    help = 'Import OBD-II error codes from provided data'

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', help='Reset existing data before import')

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write(self.style.WARNING('Deleting existing error codes...'))
            ErrorCode.objects.all().delete()
            ErrorCodeCategory.objects.all().delete()
        
        # إنشاء فئات الأكواد
        categories = [
            {
                'code_prefix': 'P0',
                'name': 'Generic Powertrain Codes',
                'category_type': 'ENGINE',
                'description': 'أكواد عامة للمحرك ونظام التحكم به'
            },
            {
                'code_prefix': 'P1',
                'name': 'Manufacturer-Specific Powertrain Codes',
                'category_type': 'ENGINE',
                'description': 'أكواد خاصة بالشركة المصنعة للمحرك'
            },
            {
                'code_prefix': 'P2',
                'name': 'Generic Powertrain Codes',
                'category_type': 'ENGINE',
                'description': 'أكواد عامة للمحرك - نطاق موسع'
            },
            {
                'code_prefix': 'P0100-P0199',
                'name': 'Fuel and Air Metering',
                'category_type': 'FUEL',
                'description': 'أكواد متعلقة بأنظمة الوقود والهواء'
            },
            {
                'code_prefix': 'P0200-P0299',
                'name': 'Fuel and Air Metering (Injector Circuit)',
                'category_type': 'FUEL',
                'description': 'أكواد متعلقة بدائرة الحاقن - نظام الوقود'
            },
            {
                'code_prefix': 'P0300-P0399',
                'name': 'Ignition System or Misfire',
                'category_type': 'IGNITION',
                'description': 'أكواد متعلقة بنظام الإشعال أو خلل في الاحتراق'
            },
            {
                'code_prefix': 'P0400-P0499',
                'name': 'Auxiliary Emissions Controls',
                'category_type': 'EMISSION',
                'description': 'أكواد متعلقة بأنظمة التحكم في الانبعاثات المساعدة'
            },
            {
                'code_prefix': 'P0500-P0599',
                'name': 'Vehicle Speed Controls and Idle Control System',
                'category_type': 'ENGINE',
                'description': 'أكواد متعلقة بأنظمة التحكم في سرعة السيارة والتباطؤ'
            },
            {
                'code_prefix': 'P0600-P0699',
                'name': 'Computer Output Circuit',
                'category_type': 'ELECTRICAL',
                'description': 'أكواد متعلقة بدوائر إخراج الكمبيوتر'
            },
            {
                'code_prefix': 'P0700-P0899',
                'name': 'Transmission',
                'category_type': 'TRANSMISSION',
                'description': 'أكواد متعلقة بناقل الحركة'
            }
        ]
        
        # إنشاء كائنات الفئات
        for category_data in categories:
            category, created = ErrorCodeCategory.objects.get_or_create(
                code_prefix=category_data['code_prefix'],
                defaults={
                    'name': category_data['name'],
                    'category_type': category_data['category_type'],
                    'description': category_data['description']
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Category exists: {category.name}'))
        
        # استيراد الأكواد من البيانات المقدمة
        # نموذج للأكواد من البيانات
        codes_data = [
            {
                'obd_code': 'P0300',
                'description': 'Random/Multiple Cylinder Misfire Detected',
                'severity': 'HIGH',
                'repair_difficulty': 'MEDIUM',
                'emergency_action': 'Reduce speed and avoid heavy acceleration',
                'category_prefix': 'P0300-P0399'
            },
            {
                'obd_code': 'P0301',
                'description': 'Cylinder 1 Misfire Detected',
                'severity': 'MEDIUM',
                'repair_difficulty': 'MEDIUM',
                'emergency_action': 'Service soon',
                'category_prefix': 'P0300-P0399'
            },
            {
                'obd_code': 'P0171',
                'description': 'System Too Lean (Bank 1)',
                'severity': 'MEDIUM',
                'repair_difficulty': 'MEDIUM',
                'emergency_action': 'Can continue driving, but service soon',
                'category_prefix': 'P0100-P0199'
            },
            {
                'obd_code': 'P0420',
                'description': 'Catalyst System Efficiency Below Threshold (Bank 1)',
                'severity': 'MEDIUM',
                'repair_difficulty': 'HARD',
                'emergency_action': 'Can continue driving, but will impact emissions',
                'category_prefix': 'P0400-P0499'
            },
            # يمكن إضافة المزيد من الأكواد
        ]
        
        # إضافة أكواد من البيانات المقدمة
        counter = 0
        for code_data in codes_data:
            try:
                category = ErrorCodeCategory.objects.get(code_prefix=code_data['category_prefix'])
                error_code, created = ErrorCode.objects.get_or_create(
                    obd_code=code_data['obd_code'],
                    defaults={
                        'category': category,
                        'description': code_data['description'],
                        'severity': code_data['severity'],
                        'repair_difficulty': code_data['repair_difficulty'],
                        'emergency_action': code_data['emergency_action']
                    }
                )
                
                if created:
                    counter += 1
                    self.stdout.write(self.style.SUCCESS(f'Added error code: {error_code.obd_code}'))
            except ErrorCodeCategory.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Category not found for code: {code_data["obd_code"]}'))
        
        # تحليل الأكواد من النص المقدم في البيانات
        code_pattern = re.compile(r'(P\d{4})\s*–\s*(.+)')
        
        # هذا مجرد مثال لكيفية تحليل النص من البيانات المقدمة
        sample_text = """
        P0300 – Engine Misfire Detected
        P0301 – Cylinder 1 Misfire Detected
        P0302 – Cylinder 2 Misfire Detected
        P0420 – Catalyst System Low Efficiency
        """
        
        matches = code_pattern.findall(sample_text)
        for obd_code, description in matches:
            # تحديد الفئة الملائمة
            category = None
            code_num = int(obd_code[1:])
            
            if 100 <= code_num <= 199:
                category_prefix = 'P0100-P0199'
            elif 200 <= code_num <= 299:
                category_prefix = 'P0200-P0299'
            elif 300 <= code_num <= 399:
                category_prefix = 'P0300-P0399'
            elif 400 <= code_num <= 499:
                category_prefix = 'P0400-P0499'
            elif 500 <= code_num <= 599:
                category_prefix = 'P0500-P0599'
            elif 600 <= code_num <= 699:
                category_prefix = 'P0600-P0699'
            elif 700 <= code_num <= 899:
                category_prefix = 'P0700-P0899'
            else:
                category_prefix = 'P0'
            
            try:
                category = ErrorCodeCategory.objects.get(code_prefix=category_prefix)
                
                # تحديد الخطورة بناءً على نوع الكود
                severity = 'MEDIUM'  # افتراضي
                if 'misfire' in description.lower():
                    severity = 'HIGH'
                elif 'catalyst' in description.lower():
                    severity = 'MEDIUM'
                
                error_code, created = ErrorCode.objects.get_or_create(
                    obd_code=obd_code,
                    defaults={
                        'category': category,
                        'description': description.strip(),
                        'severity': severity,
                        'repair_difficulty': 'MEDIUM',  # افتراضي
                        'emergency_action': None
                    }
                )
                
                if created:
                    counter += 1
                    self.stdout.write(self.style.SUCCESS(f'Added error code from text: {error_code.obd_code}'))
            except ErrorCodeCategory.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Category not found for code: {obd_code}'))
        
        self.stdout.write(self.style.SUCCESS(f'Successfully imported {counter} error codes'))