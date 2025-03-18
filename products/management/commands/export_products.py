# filepath: /kkihome/home/t22cs007/myDjango/render_test/products/management/commands/export_products.py
import csv
from django.core.management.base import BaseCommand
from products.models import Product

class Command(BaseCommand):
    help = 'Export products to a text file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='The path to the text file to save product data')

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        products = Product.objects.all()
        with open(file_path, 'w', encoding='utf-8') as file:
            writer = csv.writer(file)
            for product in products:
                writer.writerow([product.name, product.category, product.quantity])
        self.stdout.write(self.style.SUCCESS('Successfully exported products to file'))