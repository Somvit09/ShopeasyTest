from django.shortcuts import render, redirect
from carts.models import CartItem
from .forms import OrderForm
from .models import Order, Payment, Order_product
import datetime
import json
from carts.models import Product
from django.http import JsonResponse
# email verification
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.template.loader import render_to_string


# Create your views here.

def place_order(request, total=0, quantity=0):
    # # at first we need to see if the user has anything in cart, if not then redirect to store
    user = request.user
    cart = CartItem.objects.filter(user=user)
    if cart.count() <= 0:
        return redirect('storeHome')

    grand_total = 0
    tax = 0
    for i in cart:
        total += (i.product.price * i.quantity)
        quantity += i.quantity
    tax = int(total * (2.25 / 100))
    grand_total = int(tax + total)
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            # Store all the billing information inside Order table
            data = Order()
            data.user = user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')  # get the ip of the user
            data.save()
            # Generate order number
            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            # creating order object
            order = Order.objects.get(user=user, is_ordered=False, order_number=order_number)
            instance = dict(
                order=order, cart_items=cart, total=total, grand_total=grand_total, tax=tax,
            )
            return render(request, 'order/payments.html', instance)

    return render(request, 'order/place-order.html')


def payment(request):
    body = json.loads(request.body)
    # store details in the payment model
    user = request.user
    order = Order.objects.get(user=user, order_number=body['orderId'], is_ordered=False)
    pay_obj = Payment(
        user=user,
        payment_id=body['transactionId'],
        payment_method=body['payment_method'],
        status=body['transactionStatus'],
        amount_paid=order.order_total,
    )
    pay_obj.save()
    order.payment = pay_obj
    order.is_ordered = True
    order.save()

    # now we have to save the order and payment details in order_product model
    cart_items = CartItem.objects.filter(user=user)
    for items in cart_items:
        order_product = Order_product()
        order_product.user_id = user.id
        order_product.order_id = order.id
        order_product.payment = pay_obj
        order_product.product_id = items.product_id
        order_product.quantity = items.quantity
        order_product.product_price = items.product.price
        order_product.is_ordered = True
        order_product.save()

        # now get the variations to save with the order
        cart_item = CartItem.objects.get(id=items.id)
        variations = cart_item.variations.all()
        orderproduct = Order_product.objects.get(id=order_product.id)
        orderproduct.variations.set(variations)
        orderproduct.save()

        # now we have to reduce the stock of that product after a successful order
        product = Product.objects.get(id=items.product_id)
        product.stock -= items.quantity
        product.save()

    # after a successful order we have to delete the cart items for that particular user
    CartItem.objects.filter(user=user).delete()

    # after that we have to send mail to that user about the order and transaction information
    mail_subject = "Order Id and Transaction Id verification"
    message = render_to_string('order/order_verification.html', dict(
        user=user,
        order=order,
        payment=pay_obj,
    ))
    mail = user.email
    send_mail = EmailMessage(mail_subject, message, to=[mail, ])
    send_mail.send()

    # now send back to the function by json data response
    data = dict(
        order_number=order.order_number,
        transaction_id=pay_obj.payment_id,
    )
    return JsonResponse(data)


def payment_success(request):
    order_number = request.GET.get('order_number')
    payment_id = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number)
        order_product = Order_product.objects.filter(order_id=order.id)
        payment_id = Payment.objects.get(payment_id=payment_id)
        subtotal = 0
        for i in order_product:
            subtotal += i.product_price * i.quantity
        data = dict(
            order=order,
            order_product=order_product,
            transaction_id=payment_id.payment_id,
            payment=payment_id,
            subtotal=subtotal,
        )
        return render(request, 'order/order_complete.html', data)
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('home')