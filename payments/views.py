from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib import messages
from shop.models import Product, Customer, Order, OrderItem
from .models import Payment
import razorpay
import json


def get_razorpay_client():
    """Get Razorpay client instance"""
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@require_POST
def create_order(request):
    """Create Razorpay order and save order in database"""
    try:
        data = json.loads(request.body)
        
        # Get cart items
        cart = request.session.get('cart', {})
        if not cart:
            return JsonResponse({'success': False, 'message': 'Cart is empty'}, status=400)
        
        # Calculate totals
        subtotal = 0
        order_items = []
        
        for product_id, quantity in cart.items():
            try:
                product = Product.objects.get(id=product_id, is_active=True)
                item_total = float(product.display_price) * quantity
                subtotal += item_total
                order_items.append({
                    'product': product,
                    'quantity': quantity,
                    'price': float(product.display_price),
                })
            except Product.DoesNotExist:
                continue
        
        if not order_items:
            return JsonResponse({'success': False, 'message': 'No valid items in cart'}, status=400)
        
        shipping_charge = 0 if subtotal >= 500 else 50
        total = subtotal + shipping_charge
        
        # Create or get customer
        customer, created = Customer.objects.get_or_create(
            email=data.get('email'),
            defaults={
                'name': data.get('name'),
                'phone': data.get('phone'),
                'address': data.get('address'),
                'city': data.get('city'),
                'state': data.get('state'),
                'pincode': data.get('pincode'),
            }
        )
        
        if not created:
            # Update existing customer info
            customer.name = data.get('name')
            customer.phone = data.get('phone')
            customer.address = data.get('address')
            customer.city = data.get('city')
            customer.state = data.get('state')
            customer.pincode = data.get('pincode')
            customer.save()
        
        # Create order in database
        shipping_address = f"{data.get('address')}, {data.get('city')}, {data.get('state')} - {data.get('pincode')}"
        order = Order.objects.create(
            customer=customer,
            subtotal=subtotal,
            shipping_charge=shipping_charge,
            total=total,
            shipping_address=shipping_address,
            notes=data.get('notes', ''),
        )
        
        # Create order items
        for item in order_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                product_name=item['product'].name,
                price=item['price'],
                quantity=item['quantity'],
            )
        
        # Create Razorpay order
        client = get_razorpay_client()
        razorpay_order = client.order.create({
            'amount': int(total * 100),  # Amount in paise
            'currency': 'INR',
            'receipt': order.order_id,
            'notes': {
                'order_id': order.order_id,
                'customer_name': customer.name,
            }
        })
        
        # Update order with Razorpay order ID
        order.razorpay_order_id = razorpay_order['id']
        order.save()
        
        # Create payment record
        Payment.objects.create(
            order=order,
            razorpay_order_id=razorpay_order['id'],
            amount=total,
        )
        
        return JsonResponse({
            'success': True,
            'order_id': order.order_id,
            'razorpay_order_id': razorpay_order['id'],
            'amount': int(total * 100),
            'currency': 'INR',
            'key_id': settings.RAZORPAY_KEY_ID,
            'customer': {
                'name': customer.name,
                'email': customer.email,
                'phone': customer.phone,
            }
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@csrf_exempt
@require_POST
def verify_payment(request):
    """Verify Razorpay payment signature"""
    try:
        data = json.loads(request.body)
        
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')
        
        # Verify signature
        client = get_razorpay_client()
        params = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature,
        }
        
        try:
            client.utility.verify_payment_signature(params)
            
            # Update order and payment
            order = Order.objects.get(razorpay_order_id=razorpay_order_id)
            order.razorpay_payment_id = razorpay_payment_id
            order.razorpay_signature = razorpay_signature
            order.payment_status = 'PAID'
            order.status = 'CONFIRMED'
            order.save()
            
            # Update payment record
            payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
            payment.razorpay_payment_id = razorpay_payment_id
            payment.razorpay_signature = razorpay_signature
            payment.status = 'CAPTURED'
            payment.save()
            
            # Clear cart
            request.session['cart'] = {}
            request.session.modified = True
            
            return JsonResponse({
                'success': True,
                'message': 'Payment successful!',
                'order_id': order.order_id,
            })
            
        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({
                'success': False,
                'message': 'Payment verification failed!',
            }, status=400)
            
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


def payment_success(request):
    """Payment success page"""
    order_id = request.GET.get('order_id')
    order = None
    if order_id:
        try:
            order = Order.objects.get(order_id=order_id)
        except Order.DoesNotExist:
            pass
    
    context = {
        'order': order,
        'whatsapp_number': settings.WHATSAPP_NUMBER,
    }
    return render(request, 'payments/success.html', context)


def payment_failed(request):
    """Payment failed page"""
    context = {
        'whatsapp_number': settings.WHATSAPP_NUMBER,
    }
    return render(request, 'payments/failed.html', context)
