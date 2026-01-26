"""
Sample data for GiftWorld
Run this script to populate the database with sample products, categories, and testimonials.
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'giftworld_project.settings')
django.setup()

from shop.models import Category, Product, Testimonial


def create_sample_data():
    print("Creating sample data...")
    
    # Create Categories
    categories_data = [
        {'name': 'Gift Boxes', 'description': 'Premium handcrafted gift boxes for all occasions'},
        {'name': 'Flowers', 'description': 'Beautiful flower arrangements and bouquets'},
        {'name': 'Photo Frames', 'description': 'Customizable photo frames to capture memories'},
        {'name': 'Hampers', 'description': 'Luxury gift hampers with curated items'},
        {'name': 'Personalized', 'description': 'Custom personalized gifts with names and messages'},
    ]
    
    categories = {}
    for cat_data in categories_data:
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        categories[cat_data['name']] = category
        print(f"  {'Created' if created else 'Found'} category: {cat_data['name']}")
    
    # Create Products
    products_data = [
        {
            'name': 'Blush Bloom',
            'category': 'Gift Boxes',
            'description': 'A delicate pink-themed gift box featuring premium chocolates, scented candles, and beautiful dried flowers. Perfect for expressing love and appreciation.',
            'short_description': 'Elegant pink gift box',
            'price': 1299,
            'badge': 'NEW',
            'stock': 15,
            'is_featured': True,
        },
        {
            'name': 'Dune Beige',
            'category': 'Gift Boxes',
            'description': 'Sophisticated beige and gold themed luxury gift box with artisan chocolates, premium tea, and handmade accessories. An elegant choice for special occasions.',
            'short_description': 'Luxury beige collection',
            'price': 1599,
            'stock': 20,
            'is_featured': True,
        },
        {
            'name': 'Peony Roses',
            'category': 'Flowers',
            'description': 'Stunning arrangement of fresh peony roses in soft pink hues. Hand-arranged by our expert florists for maximum beauty and longevity.',
            'short_description': 'Fresh pink peonies',
            'price': 899,
            'stock': 10,
            'is_featured': True,
        },
        {
            'name': 'Wild Whisper',
            'category': 'Flowers',
            'description': 'A whimsical wildflower bouquet featuring a mix of seasonal blooms in natural, earthy tones. Perfect for nature lovers.',
            'short_description': 'Wildflower bouquet',
            'price': 799,
            'badge': 'POPULAR',
            'stock': 12,
            'is_featured': True,
        },
        {
            'name': 'Memory Lane Frame',
            'category': 'Photo Frames',
            'description': 'Beautiful handcrafted wooden photo frame with engraving option. Perfect for capturing your precious memories.',
            'short_description': 'Engraved wooden frame',
            'price': 599,
            'discount_price': 499,
            'stock': 25,
        },
        {
            'name': 'Premium Anniversary Hamper',
            'category': 'Hampers',
            'description': 'Luxurious anniversary hamper featuring champagne glasses, premium chocolates, scented candles, and a beautiful greeting card.',
            'short_description': 'Complete anniversary gift',
            'price': 2499,
            'badge': 'BESTSELLER',
            'stock': 8,
            'is_featured': True,
        },
        {
            'name': 'Personalized Name Lamp',
            'category': 'Personalized',
            'description': 'Custom LED lamp with 3D engraved name. Energy-efficient and makes a stunning night light or desk decoration.',
            'short_description': 'Custom LED name lamp',
            'price': 699,
            'stock': 30,
        },
        {
            'name': 'Valentine Special Box',
            'category': 'Gift Boxes',
            'description': 'Heart-shaped gift box filled with premium chocolates, teddy bear, and love-themed accessories. The perfect Valentine surprise.',
            'short_description': 'Romantic heart box',
            'price': 1899,
            'badge': 'LIMITED',
            'stock': 5,
        },
    ]
    
    for prod_data in products_data:
        category = categories[prod_data.pop('category')]
        product, created = Product.objects.get_or_create(
            name=prod_data['name'],
            defaults={**prod_data, 'category': category}
        )
        print(f"  {'Created' if created else 'Found'} product: {prod_data['name']}")
    
    # Create Testimonials
    testimonials_data = [
        {
            'customer_name': 'Priya Sharma',
            'content': 'The gift box was absolutely stunning! My husband loved the anniversary surprise. The packaging was premium and delivery was on time.',
            'rating': 5,
            'occasion': 'Anniversary Gift',
            'is_featured': True,
        },
        {
            'customer_name': 'Rahul Verma',
            'content': 'Ordered a birthday hamper for my mother and she was thrilled. The quality of items exceeded my expectations. Will definitely order again!',
            'rating': 5,
            'occasion': 'Birthday Gift',
            'is_featured': True,
        },
        {
            'customer_name': 'Anita Kumari',
            'content': 'Beautiful flower arrangement! Fresh and fragrant. The delivery guy was very professional. Highly recommend GiftWorld!',
            'rating': 5,
            'occasion': 'Valentine\'s Day',
            'is_featured': True,
        },
        {
            'customer_name': 'Amit Singh',
            'content': 'Got a personalized lamp for my daughter and she absolutely loves it. Amazing quality and fast delivery to Purnea.',
            'rating': 5,
            'occasion': 'Birthday Gift',
        },
    ]
    
    for test_data in testimonials_data:
        testimonial, created = Testimonial.objects.get_or_create(
            customer_name=test_data['customer_name'],
            defaults=test_data
        )
        print(f"  {'Created' if created else 'Found'} testimonial: {test_data['customer_name']}")
    
    print("\n✅ Sample data created successfully!")
    print(f"   Categories: {Category.objects.count()}")
    print(f"   Products: {Product.objects.count()}")
    print(f"   Testimonials: {Testimonial.objects.count()}")


if __name__ == '__main__':
    create_sample_data()
