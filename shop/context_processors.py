from django.conf import settings


def cart_context(request):
    """Add cart count to all templates"""
    cart = request.session.get('cart', {})
    cart_count = sum(cart.values()) if cart else 0
    
    return {
        'cart_count': cart_count,
        'whatsapp_number': getattr(settings, 'WHATSAPP_NUMBER', '+917542043169'),
    }
