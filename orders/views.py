from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.conf import settings
from .models import Order, Product

def order_form(request):
    products = Product.objects.all()
    if request.method == 'POST':
        customer_name = request.POST.get('customer_name')
        customer_id = request.POST.get('customer_id')
        quantity = request.POST.get('quantity')
        product_id = request.POST.get('product')
        user_email = request.POST.get('user_email')
        
        product = Product.objects.get(id=product_id)
        product_cost = product.cost * int(quantity)
        
        order = Order.objects.create(
            customer_name=customer_name,
            customer_id=customer_id,
            quantity=quantity,
            product=product,
            product_cost=product_cost,
            user_email=user_email,
            status='Order Placed'
        )
        
        # Send email to warehouse
        subject = f'New Order #{order.id}'
        confirm_url = request.build_absolute_uri(f"/order/{order.id}/confirm/")
        message = f"""
        New Order Details:<br>
        Customer Name: {customer_name}<br>
        Customer ID: {customer_id}<br>
        Product: {product.name}<br>
        Quantity: {quantity}<br>
        Total Cost: {product_cost}<br>
        User Email: {user_email}<br><br>

        <a href="{confirm_url}">Confirm Order</a>
        """
        send_mail(
            subject,
            '',
            settings.DEFAULT_FROM_EMAIL,
            [settings.WAREHOUSE_EMAIL],
            html_message=message,
        )
        
        # Pass success message to template for SweetAlert
        return render(request, 'orders/order_form.html', {
            'products': products,
            'message': 'Order placed successfully! Warehouse has been notified.'
        })
    
    return render(request, 'orders/order_form.html', {'products': products})

def confirm_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        order.status = 'Confirmed'
        order.save()
        
        # Send confirmation email to user
        send_mail(
            f'Order #{order.id} Confirmed',
            f'Your order #{order.id} is ready to dispatch.',
            settings.DEFAULT_FROM_EMAIL,
            [order.user_email],
        )
        
        # Pass success message to template for SweetAlert
        return render(request, 'orders/order_form.html', {
            'products': Product.objects.all(),
            'message': 'Order confirmed and user notified.'
        })
    except Order.DoesNotExist:
        # Handle invalid order ID
        return render(request, 'orders/order_form.html', {
            'products': Product.objects.all(),
            'message': 'Error: Order not found.'
        })