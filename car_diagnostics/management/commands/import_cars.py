import csv
from django.core.management.base import BaseCommand
from car_diagnostics.models import CarBrand, Car

class Command(BaseCommand):
    help = 'Import car makes and models from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')
        parser.add_argument('--reset', action='store_true', help='Reset existing data before import')

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write(self.style.WARNING('Deleting existing car data...'))
            Car.objects.all().delete()
            CarBrand.objects.all().delete()
        
        csv_file_path = options['csv_file']
        
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            brands_count = 0
            models_count = 0
            
            for row in reader:
                # إنشاء أو الحصول على الشركة المصنعة
                brand, brand_created = CarBrand.objects.get_or_create(
                    name=row['brand']
                )
                
                if brand_created:
                    brands_count += 1
                
                # إنشاء موديل السيارة
                car, car_created = Car.objects.get_or_create(
                    brand=brand,
                    model=row['model'],
                    year=int(row['year']),
                    engine_type=row['engine_type'],
                    defaults={
                        'common_issues': row.get('common_issues', '')
                    }
                )
                
                if car_created:
                    models_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully imported {brands_count} brands and {models_count} car models')
            )