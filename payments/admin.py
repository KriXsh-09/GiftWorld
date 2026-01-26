from django.contrib import admin
from .models import Payment, Refund


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'razorpay_payment_id', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order__order_id', 'razorpay_payment_id', 'razorpay_order_id']
    readonly_fields = ['razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature']


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ['payment', 'razorpay_refund_id', 'amount', 'created_at']
    search_fields = ['razorpay_refund_id', 'payment__order__order_id']
