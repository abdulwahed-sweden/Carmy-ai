# car_diagnostics/management/commands/import_initial_data.py
import csv
import os
from django.core.management.base import BaseCommand
from django.core.files import File
from car_diagnostics.models import CarBrand, Car, ErrorCodeCategory, ErrorCode, CarError, RepairResource

class Command(BaseCommand):
    help = 'Import initial data for car diagnostics'

    def handle(self, *args, **options):
        self.stdout.write('Importing initial data...')
        
        # Create error code categories
        self.create_error_categories()
        
        # Create some common error codes
        self.create_error_codes()
        
        # Create car brands and models
        self.create_car_brands()
        
        self.stdout.write(self.style.SUCCESS('Successfully imported initial data'))
    
    def create_error_categories(self):
        categories = [
            {
                'code_prefix': 'P0100-P0199',
                'name': 'Fuel and Air Metering',
                'category_type': 'FUEL',
                'description': 'Codes related to fuel and air metering systems, including oxygen sensors and fuel injectors.'
            },
            {
                'code_prefix': 'P0200-P0299',
                'name': 'Fuel and Air Metering (Injector Circuit)',
                'category_type': 'FUEL',
                'description': 'Codes related to fuel injector circuits and related components.'
            },
            
            {
                'code_prefix': 'P0300-P0399',
                'name': 'Ignition System or Misfire',
                'category_type': 'IGNITION',
                'description': 'Codes related to engine misfires and ignition system issues.'
            },
            {
                'code_prefix': 'P0400-P0499',
                'name': 'Auxiliary Emissions Controls',
                'category_type': 'EMISSION',
                'description': 'Codes related to emission control systems, including EGR and catalytic converters.'
            },
            {
                'code_prefix': 'P0500-P0599',
                'name': 'Vehicle Speed Controls and Idle Control System',
                'category_type': 'ENGINE',
                'description': 'Codes related to vehicle speed sensors, idle control, and cruise control systems.'
            },
            {
                'code_prefix': 'P0600-P0699',
                'name': 'Computer Output Circuit',
                'category_type': 'ELECTRICAL',
                'description': 'Codes related to computer output circuits and internal controller failures.'
            },
            {
                'code_prefix': 'P0700-P0899',
                'name': 'Transmission',
                'category_type': 'TRANSMISSION',
                'description': 'Codes related to automatic and manual transmission systems and controls.'
            },
        ]
        
        for cat_data in categories:
            ErrorCodeCategory.objects.get_or_create(
                code_prefix=cat_data['code_prefix'],
                defaults={
                    'name': cat_data['name'],
                    'category_type': cat_data['category_type'],
                    'description': cat_data['description']
                }
            )
        
        self.stdout.write(f'Created {len(categories)} error code categories')
    
    def create_error_codes(self):
        # Common error codes to add
        codes_data = [
            {
                'obd_code': 'P0300',
                'category_prefix': 'P0300-P0399',
                'description': 'Random/Multiple Cylinder Misfire Detected',
                'severity': 'HIGH',
                'repair_difficulty': 'MEDIUM',
                'emergency_action': 'Reduce speed and avoid heavy acceleration. Have vehicle inspected as soon as possible.'
            },
            {
                'obd_code': 'P0301',
                'category_prefix': 'P0300-P0399',
                'description': 'Cylinder 1 Misfire Detected',
                'severity': 'MEDIUM',
                'repair_difficulty': 'MEDIUM',
                'emergency_action': 'Have vehicle inspected soon to prevent catalytic converter damage.'
            },
            {
                'obd_code': 'P0171',
                'category_prefix': 'P0100-P0199',
                'description': 'System Too Lean (Bank 1)',
                'severity': 'MEDIUM',
                'repair_difficulty': 'MEDIUM',
                'emergency_action': 'Safe to drive, but have diagnosed soon to prevent performance issues.'
            },
            {
                'obd_code': 'P0420',
                'category_prefix': 'P0400-P0499',
                'description': 'Catalyst System Efficiency Below Threshold (Bank 1)',
                'severity': 'MEDIUM',
                'repair_difficulty': 'HARD',
                'emergency_action': 'Safe to drive, but have diagnosed to prevent emissions problems.'
            },
            {
                'obd_code': 'P0700',
                'category_prefix': 'P0700-P0899',
                'description': 'Transmission Control System Malfunction',
                'severity': 'HIGH',
                'repair_difficulty': 'HARD',
                'emergency_action': 'Have vehicle inspected immediately. May lead to transmission failure.'
            },
        ]
        
        codes_created = 0
        for code_data in codes_data:
            try:
                category = ErrorCodeCategory.objects.get(code_prefix=code_data['category_prefix'])
                
                ErrorCode.objects.get_or_create(
                    obd_code=code_data['obd_code'],
                    defaults={
                        'category': category,
                        'description': code_data['description'],
                        'severity': code_data['severity'],
                        'repair_difficulty': code_data['repair_difficulty'],
                        'emergency_action': code_data['emergency_action']
                    }
                )
                codes_created += 1
            except ErrorCodeCategory.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Category not found for code: {code_data['obd_code']}"))
        
        self.stdout.write(f'Created {codes_created} error codes')
    
    def create_car_brands(self):
        # Create some major car brands
        brands_data = [
            {'name': 'Toyota'},
            {'name': 'Honda'},
            {'name': 'Ford'},
            {'name': 'Chevrolet'},
            {'name': 'Nissan'},
            {'name': 'Hyundai'},
            {'name': 'BMW'},
            {'name': 'Mercedes-Benz'},
            {'name': 'Audi'},
            {'name': 'Volkswagen'},
        ]
        
        brands_created = 0
        for brand_data in brands_data:
            CarBrand.objects.get_or_create(
                name=brand_data['name'],
                defaults=brand_data
            )
            brands_created += 1
        
        self.stdout.write(f'Created {brands_created} car brands')
        
        # Create some car models
        cars_data = [
            {
                'brand_name': 'Toyota',
                'model': 'Camry',
                'year': 2023,
                'engine_type': 'Gasoline 2.5L',
                'common_issues': 'Occasional transmission hesitation, minor electrical issues.'
            },
            {
                'brand_name': 'Toyota',
                'model': 'Corolla',
                'year': 2022,
                'engine_type': 'Gasoline 1.8L',
                'common_issues': 'Some reports of fuel system issues, occasional misfire.'
            },
            {
                'brand_name': 'Honda',
                'model': 'Accord',
                'year': 2023,
                'engine_type': 'Gasoline 1.5L Turbo',
                'common_issues': 'Turbo-related issues, minor transmission concerns.'
            },
            {
                'brand_name': 'Honda',
                'model': 'Civic',
                'year': 2022,
                'engine_type': 'Gasoline 2.0L',
                'common_issues': 'Reported AC system issues, occasional electrical problems.'
            },
            {
                'brand_name': 'Ford',
                'model': 'F-150',
                'year': 2023,
                'engine_type': 'V8 5.0L',
                'common_issues': 'Occasional transmission shudder, electrical system glitches.'
            },
        ]
        
        cars_created = 0
        for car_data in cars_data:
            try:
                brand = CarBrand.objects.get(name=car_data['brand_name'])
                
                Car.objects.get_or_create(
                    brand=brand,
                    model=car_data['model'],
                    year=car_data['year'],
                    engine_type=car_data['engine_type'],
                    defaults={
                        'common_issues': car_data['common_issues']
                    }
                )
                cars_created += 1
            except CarBrand.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Brand not found for car: {car_data['model']}"))
        
        self.stdout.write(f'Created {cars_created} car models')
        
        # Create car-specific error codes
        self.create_car_errors()
    
    def create_car_errors(self):
        # Map some errors to specific cars with custom solutions
        car_errors_data = [
            {
                'brand': 'Toyota',
                'model': 'Camry',
                'year': 2023,
                'obd_code': 'P0300',
                'common_causes': 'Faulty ignition coils, worn spark plugs, vacuum leaks, fuel injector issues.',
                'solutions': 'Inspect and replace spark plugs, check ignition coils, perform fuel injector cleaning.',
                'repair_steps': '1. Check spark plugs for wear.\n2. Test ignition coils with multimeter.\n3. Check for vacuum leaks.\n4. Test fuel injectors.',
                'estimated_cost': '$150-300 depending on required parts'
            },
            {
                'brand': 'Toyota',
                'model': 'Camry',
                'year': 2023,
                'obd_code': 'P0171',
                'common_causes': 'Vacuum leaks, dirty MAF sensor, clogged fuel injectors, faulty oxygen sensors.',
                'solutions': 'Inspect for vacuum leaks, clean or replace MAF sensor, check and replace oxygen sensors if needed.',
                'repair_steps': '1. Check for vacuum leaks around intake manifold.\n2. Clean MAF sensor with MAF cleaner.\n3. Check fuel pressure.\n4. Inspect and test oxygen sensors.',
                'estimated_cost': '$100-250 depending on required parts'
            },
            {
                'brand': 'Honda',
                'model': 'Civic',
                'year': 2022,
                'obd_code': 'P0300',
                'common_causes': 'Ignition coil failure, fouled spark plugs, vacuum leak, fuel delivery issues.',
                'solutions': 'Replace spark plugs, check ignition coils and fuel injectors, inspect for vacuum leaks.',
                'repair_steps': '1. Replace spark plugs.\n2. Test ignition coils.\n3. Check fuel pressure.\n4. Inspect intake manifold for leaks.',
                'estimated_cost': '$120-280 depending on required parts'
            },
            {
                'brand': 'Honda',
                'model': 'Accord',
                'year': 2023,
                'obd_code': 'P0420',
                'common_causes': 'Failing catalytic converter, exhaust leaks, oxygen sensor failure, engine misfire.',
                'solutions': 'Check for exhaust leaks, test oxygen sensors, inspect catalytic converter, check for engine misfires.',
                'repair_steps': '1. Check for exhaust leaks.\n2. Test oxygen sensors.\n3. Inspect catalytic converter.\n4. Check for related trouble codes.',
                'estimated_cost': '$400-1200 depending on if catalytic converter replacement is needed'
            },
            {
                'brand': 'Ford',
                'model': 'F-150',
                'year': 2023,
                'obd_code': 'P0700',
                'common_causes': 'Transmission control module issues, wiring problems, solenoid failure, low transmission fluid.',
                'solutions': 'Check transmission fluid level and condition, inspect wiring harness, test solenoids, check TCM.',
                'repair_steps': '1. Check transmission fluid level and condition.\n2. Scan for specific transmission codes.\n3. Inspect wiring harness for damage.\n4. Test transmission solenoids.\n5. Check for TCM updates.',
                'estimated_cost': '$200-1500 depending on the specific issue'
            },
        ]
        
        car_errors_created = 0
        resources_created = 0
        
        for error_data in car_errors_data:
            try:
                car = Car.objects.get(
                    brand__name=error_data['brand'],
                    model=error_data['model'],
                    year=error_data['year']
                )
                
                error_code = ErrorCode.objects.get(obd_code=error_data['obd_code'])
                
                car_error, created = CarError.objects.get_or_create(
                    car=car,
                    error_code=error_code,
                    defaults={
                        'common_causes': error_data['common_causes'],
                        'solutions': error_data['solutions'],
                        'repair_steps': error_data['repair_steps'],
                        'estimated_cost': error_data['estimated_cost']
                    }
                )
                
                if created:
                    car_errors_created += 1
                    
                    # Add some resources
                    resources = [
                        {
                            'title': f'How to Fix {error_data["obd_code"]} in {error_data["brand"]} {error_data["model"]}',
                            'resource_type': 'VIDEO',
                            'url': 'https://example.com/video'
                        },
                        {
                            'title': f'DIY Guide: Repairing {error_data["obd_code"]} Code',
                            'resource_type': 'ARTICLE',
                            'url': 'https://example.com/article'
                        }
                    ]
                    
                    for resource_data in resources:
                        RepairResource.objects.create(
                            car_error=car_error,
                            title=resource_data['title'],
                            resource_type=resource_data['resource_type'],
                            url=resource_data['url']
                        )
                        resources_created += 1
                
            except (Car.DoesNotExist, ErrorCode.DoesNotExist) as e:
                self.stdout.write(self.style.ERROR(f"Error creating car error: {str(e)}"))
        
        self.stdout.write(f'Created {car_errors_created} car-specific errors with {resources_created} resources')