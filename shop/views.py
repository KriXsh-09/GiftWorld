from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Category, Product, Testimonial, ContactEnquiry, Customer, Order, OrderItem
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, ProductForm, CategoryForm
from .utils import generate_otp, send_verification_email, verify_email_otp
from datetime import datetime, timedelta
import json


def home(request):
    """Home page view"""
    featured_products = Product.objects.filter(is_active=True, is_featured=True)[:4]
    new_products = Product.objects.filter(is_active=True, badge='NEW')[:4]
    popular_products = Product.objects.filter(is_active=True, badge='POPULAR')[:4]
    testimonials = Testimonial.objects.filter(is_active=True, is_featured=True)[:3]
    categories = Category.objects.filter(is_active=True)[:6]
    
    # If not enough featured products, fill with recent ones
    if featured_products.count() < 4:
        featured_products = Product.objects.filter(is_active=True)[:4]
    
    context = {
        'featured_products': featured_products,
        'new_products': new_products,
        'popular_products': popular_products,
        'testimonials': testimonials,
        'categories': categories,
        'whatsapp_number': settings.WHATSAPP_NUMBER,
    }
    return render(request, 'shop/home.html', context)


def shop(request):
    """Shop page with all products"""
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)
    
    # Filter by category if provided
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    # Filter by badge
    badge = request.GET.get('badge')
    if badge:
        products = products.filter(badge=badge)
    
    # Sort products
    sort = request.GET.get('sort', '-created_at')
    if sort in ['price', '-price', 'name', '-name', '-created_at']:
        products = products.order_by(sort)
    
    context = {
        'products': products,
        'categories': categories,
        'current_category': category_slug,
        'current_sort': sort,
        'whatsapp_number': settings.WHATSAPP_NUMBER,
    }
    return render(request, 'shop/shop.html', context)


def product_detail(request, slug):
    """Product detail page"""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(
        category=product.category, 
        is_active=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products,
        'whatsapp_number': settings.WHATSAPP_NUMBER,
    }
    return render(request, 'shop/product_detail.html', context)


def category_detail(request, slug):
    """Category detail page"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    products = Product.objects.filter(category=category, is_active=True)
    
    context = {
        'category': category,
        'products': products,
        'whatsapp_number': settings.WHATSAPP_NUMBER,
    }
    return render(request, 'shop/category_detail.html', context)


def about(request):
    """About page"""
    testimonials = Testimonial.objects.filter(is_active=True)[:6]
    context = {
        'testimonials': testimonials,
        'whatsapp_number': settings.WHATSAPP_NUMBER,
    }
    return render(request, 'shop/about.html', context)


def contact(request):
    """Contact page"""
    if request.method == 'POST':
        try:
            enquiry = ContactEnquiry(
                name=request.POST.get('name'),
                email=request.POST.get('email'),
                phone=request.POST.get('phone'),
                subject=request.POST.get('subject'),
                message=request.POST.get('message'),
            )
            product_id = request.POST.get('product_id')
            if product_id:
                enquiry.product = Product.objects.get(id=product_id)
            enquiry.save()
            messages.success(request, 'Thank you for your enquiry! We will get back to you soon.')
            return redirect('shop:contact')
        except Exception as e:
            messages.error(request, 'Something went wrong. Please try again.')
    
    context = {
        'whatsapp_number': settings.WHATSAPP_NUMBER,
    }
    return render(request, 'shop/contact.html', context)


# ===== CART FUNCTIONALITY =====
def get_cart(request):
    """Get or create cart in session"""
    cart = request.session.get('cart', {})
    return cart


def cart_view(request):
    """View cart contents"""
    cart = get_cart(request)
    cart_items = []
    subtotal = 0
    
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            item_total = product.display_price * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total': item_total,
            })
            subtotal += item_total
        except Product.DoesNotExist:
            pass
    
    shipping_charge = 0 if subtotal >= 500 else 50  # Free shipping above ₹500
    total = subtotal + shipping_charge
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping_charge': shipping_charge,
        'total': total,
        'whatsapp_number': settings.WHATSAPP_NUMBER,
    }
    return render(request, 'shop/cart.html', context)


@require_POST
def add_to_cart(request):
    """Add product to cart"""
    try:
        data = json.loads(request.body)
        product_id = str(data.get('product_id'))
        quantity = int(data.get('quantity', 1))
        
        product = Product.objects.get(id=product_id, is_active=True)
        
        cart = get_cart(request)
        if product_id in cart:
            cart[product_id] += quantity
        else:
            cart[product_id] = quantity
        
        request.session['cart'] = cart
        request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'message': f'{product.name} added to cart!',
            'cart_count': sum(cart.values()),
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@require_POST
def update_cart(request):
    """Update cart item quantity"""
    try:
        data = json.loads(request.body)
        product_id = str(data.get('product_id'))
        quantity = int(data.get('quantity', 1))
        
        cart = get_cart(request)
        
        if quantity <= 0:
            if product_id in cart:
                del cart[product_id]
        else:
            cart[product_id] = quantity
        
        request.session['cart'] = cart
        request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'cart_count': sum(cart.values()),
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


@require_POST
def remove_from_cart(request):
    """Remove item from cart"""
    try:
        data = json.loads(request.body)
        product_id = str(data.get('product_id'))
        
        cart = get_cart(request)
        if product_id in cart:
            del cart[product_id]
        
        request.session['cart'] = cart
        request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'cart_count': sum(cart.values()),
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)


def checkout(request):
    """Checkout page"""
    cart = get_cart(request)
    if not cart:
        messages.warning(request, 'Your cart is empty!')
        return redirect('shop:shop')
    
    cart_items = []
    subtotal = 0
    
    for product_id, quantity in cart.items():
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            item_total = product.display_price * quantity
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total': item_total,
            })
            subtotal += item_total
        except Product.DoesNotExist:
            pass
    
    shipping_charge = 0 if subtotal >= 500 else 50
    total = subtotal + shipping_charge
    
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping_charge': shipping_charge,
        'total': total,
        'razorpay_key_id': settings.RAZORPAY_KEY_ID,
        'whatsapp_number': settings.WHATSAPP_NUMBER,
    }
    return render(request, 'shop/checkout.html', context)


# ===== AUTHENTICATION VIEWS =====
def user_register(request):
    '''User registration view with email OTP verification'''
    if request.user.is_authenticated:
        return redirect('shop:profile')
    
    # Check if email is already verified in session
    email_verified = request.session.get('email_verified', False)
    verified_email = request.session.get('verified_email', '')
    
    if request.method == 'POST':
        action = request.POST.get('action', '')
        
        # Step 1: Send OTP to email
        if action == 'send_otp':
            email = request.POST.get('email', '').strip()
            if not email:
                messages.error(request, 'Please enter a valid email address.')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'This email is already registered. Please use a different email or login.')
            else:
                otp = generate_otp()
                expiry = (datetime.now() + timedelta(minutes=10)).isoformat()
                
                if send_verification_email(email, otp):
                    request.session['email_otp'] = otp
                    request.session['email_otp_expiry'] = expiry
                    request.session['pending_email'] = email
                    messages.success(request, f'OTP sent to {email}. Please check your inbox.')
                else:
                    messages.error(request, 'Failed to send OTP. Please try again.')
            
            context = {
                'form': UserRegistrationForm(),
                'whatsapp_number': settings.WHATSAPP_NUMBER,
                'show_otp_input': True if request.session.get('pending_email') else False,
                'pending_email': request.session.get('pending_email', ''),
            }
            return render(request, 'shop/register.html', context)
        
        # Step 2: Verify OTP
        elif action == 'verify_otp':
            entered_otp = request.POST.get('otp', '').strip()
            session_otp = request.session.get('email_otp')
            session_expiry = request.session.get('email_otp_expiry')
            pending_email = request.session.get('pending_email')
            
            if verify_email_otp(session_otp, session_expiry, entered_otp):
                request.session['email_verified'] = True
                request.session['verified_email'] = pending_email
                # Clear OTP from session
                request.session.pop('email_otp', None)
                request.session.pop('email_otp_expiry', None)
                request.session.pop('pending_email', None)
                messages.success(request, 'Email verified successfully! Please complete your registration.')
            else:
                messages.error(request, 'Invalid or expired OTP. Please try again.')
            
            context = {
                'form': UserRegistrationForm(initial={'email': request.session.get('verified_email', '')}),
                'whatsapp_number': settings.WHATSAPP_NUMBER,
                'email_verified': request.session.get('email_verified', False),
                'verified_email': request.session.get('verified_email', ''),
            }
            return render(request, 'shop/register.html', context)
        
        # Step 3: Complete registration
        else:
            if not request.session.get('email_verified'):
                messages.error(request, 'Please verify your email first.')
                context = {
                    'form': UserRegistrationForm(),
                    'whatsapp_number': settings.WHATSAPP_NUMBER,
                }
                return render(request, 'shop/register.html', context)
            
            form = UserRegistrationForm(request.POST)
            if form.is_valid():
                # Ensure email matches verified email
                if form.cleaned_data['email'] != request.session.get('verified_email'):
                    messages.error(request, 'Email does not match the verified email.')
                else:
                    user = form.save()
                    # Clear verification session data
                    request.session.pop('email_verified', None)
                    request.session.pop('verified_email', None)
                    login(request, user)
                    messages.success(request, 'Welcome to GiftWorld! Your account has been created successfully.')
                    return redirect('shop:profile')
            
            context = {
                'form': form,
                'whatsapp_number': settings.WHATSAPP_NUMBER,
                'email_verified': True,
                'verified_email': request.session.get('verified_email', ''),
            }
            return render(request, 'shop/register.html', context)
    else:
        form = UserRegistrationForm()
        if email_verified:
            form = UserRegistrationForm(initial={'email': verified_email})
    
    context = {
        'form': form,
        'whatsapp_number': settings.WHATSAPP_NUMBER,
        'email_verified': email_verified,
        'verified_email': verified_email,
    }
    return render(request, 'shop/register.html', context)


def user_login(request):
    '''User login view'''
    if request.user.is_authenticated:
        return redirect('shop:profile')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                next_url = request.GET.get('next', 'shop:home')
                return redirect(next_url)
    else:
        form = UserLoginForm()
    
    context = {
        'form': form,
        'whatsapp_number': settings.WHATSAPP_NUMBER,
    }
    return render(request, 'shop/login.html', context)


def user_logout(request):
    '''User logout view'''
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('shop:home')


@login_required(login_url='shop:login')
def user_profile(request):
    '''User profile view'''
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('shop:profile')
    else:
        form = UserProfileForm(instance=request.user.profile)
    
    # Get user's orders
    orders = Order.objects.filter(customer__user=request.user).order_by('-created_at')[:5]
    
    context = {
        'form': form,
        'orders': orders,
        'whatsapp_number': settings.WHATSAPP_NUMBER,
    }
    return render(request, 'shop/profile.html', context)


@login_required(login_url='shop:login')
def user_orders(request):
    '''User orders history view'''
    orders = Order.objects.filter(customer__user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
        'whatsapp_number': settings.WHATSAPP_NUMBER,
    }
    return render(request, 'shop/orders.html', context)


# ===== ADMIN PRODUCT MANAGEMENT =====
def staff_required(view_func):
    '''Decorator to require staff/superuser access'''
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('shop:login')
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('shop:home')
        return view_func(request, *args, **kwargs)
    return wrapper


@staff_required
def admin_dashboard(request):
    '''Admin dashboard for product management'''
    products = Product.objects.all().order_by('-created_at')
    categories = Category.objects.all().order_by('name')
    
    context = {
        'products': products,
        'categories': categories,
        'total_products': products.count(),
        'total_categories': categories.count(),
        'active_products': products.filter(is_active=True).count(),
    }
    return render(request, 'shop/admin/dashboard.html', context)


@staff_required
def admin_add_product(request):
    '''Add a new product'''
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Product "{product.name}" added successfully!')
            return redirect('shop:admin_dashboard')
    else:
        form = ProductForm()
    
    context = {
        'form': form,
        'title': 'Add New Product',
        'action': 'Add Product',
    }
    return render(request, 'shop/admin/product_form.html', context)


@staff_required
def admin_edit_product(request, product_id):
    '''Edit an existing product'''
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('shop:admin_dashboard')
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'product': product,
        'title': f'Edit: {product.name}',
        'action': 'Update Product',
    }
    return render(request, 'shop/admin/product_form.html', context)


@staff_required
def admin_delete_product(request, product_id):
    '''Delete a product'''
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'Product "{name}" deleted successfully!')
        return redirect('shop:admin_dashboard')
    
    context = {
        'product': product,
    }
    return render(request, 'shop/admin/delete_confirm.html', context)


@staff_required
def admin_add_category(request):
    '''Add a new category'''
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save()
            messages.success(request, f'Category "{category.name}" added successfully!')
            return redirect('shop:admin_dashboard')
    else:
        form = CategoryForm()
    
    context = {
        'form': form,
        'title': 'Add New Category',
        'action': 'Add Category',
    }
    return render(request, 'shop/admin/category_form.html', context)


