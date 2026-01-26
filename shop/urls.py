from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # Product pages
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    
    # Cart
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('cart/remove/', views.remove_from_cart, name='remove_from_cart'),
    
    # Checkout
    path('checkout/', views.checkout, name='checkout'),
    
    # Authentication
    path('register/', views.user_register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.user_profile, name='profile'),
    path('orders/', views.user_orders, name='orders'),
    
    # Admin Product Management (Staff Only)
    path('manage/', views.admin_dashboard, name='admin_dashboard'),
    path('manage/product/add/', views.admin_add_product, name='admin_add_product'),
    path('manage/product/edit/<int:product_id>/', views.admin_edit_product, name='admin_edit_product'),
    path('manage/product/delete/<int:product_id>/', views.admin_delete_product, name='admin_delete_product'),
    path('manage/category/add/', views.admin_add_category, name='admin_add_category'),
]

