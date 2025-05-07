import csv
from django.core.management.base import BaseCommand
from car_diagnostics.models import ErrorCode

class Command(BaseCommand):
    help = 'Import error codes from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            counter = 0
            for row in reader:
                error_code, created = ErrorCode.objects.update_or_create(
                    obd_code=row['obd_code'],
                    defaults={
                        'description': row['description'],
                        'severity': row['severity'],
                        'system_category': row['system_category']
                    }
                )
                
                if created:
                    counter += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully imported {counter} error codes')
            )