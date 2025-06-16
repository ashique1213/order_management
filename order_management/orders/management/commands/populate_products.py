from django.core.management.base import BaseCommand
from orders.models import Product

class Command(BaseCommand):
    help = 'Populates the database with sample products'

    def handle(self, *args, **kwargs):
        products = [
            {'name': 'Laptop', 'cost': 999.99},
            {'name': 'Smartphone', 'cost': 499.99},
            {'name': 'Headphones', 'cost': 79.99},
        ]
        for product in products:
            Product.objects.get_or_create(name=product['name'], cost=product['cost'])
        self.stdout.write(self.style.SUCCESS('Successfully populated products'))