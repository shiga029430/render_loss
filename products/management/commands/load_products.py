# filepath: /kkihome/home/t22cs007/myDjango/render_test/products/management/commands/load_products.py
import csv
from django.core.management.base import BaseCommand
from products.models import Product

class Command(BaseCommand):
    help = 'Load products from a text file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='The path to the text file containing product data')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        
        Product.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Deleted all products'))
        
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                name, category = row
                Product.objects.create(name=name, category=category)
        self.stdout.write(self.style.SUCCESS('Successfully loaded products from file'))