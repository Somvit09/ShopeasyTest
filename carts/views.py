from django.shortcuts import render, redirect, get_object_or_404
from store.models import Product, VariationModel
from .models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required


# Create your views here.

def _cart_id(request):
    cart_item_session_key = request.session.session_key
    if not cart_item_session_key:
        cart_item_session_key = request.session.create()
    return cart_item_session_key


def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id)
    if current_user.is_authenticated:
        product_variation = []
        if request.method == "POST":
            for i in request.POST:
                key = i
                value = request.POST[key]
                try:
                    variation_ = VariationModel.objects.get(product=product, variation_category__iexact=key,
                                                            variation_value__iexact=value)
                    product_variation.append(variation_)
                except:
                    pass
        is_cart_item_exists = CartItem.objects.filter(user=current_user, product=product).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, user=current_user)
            existing_variation_list = []
            ids = []
            for i in cart_item:
                existing_variations = i.variations.all()
                existing_variation_list.append(list(existing_variations))
                ids.append(i.id)
            if product_variation in existing_variation_list:
                # increase the counter
                index = existing_variation_list.index(product_variation)
                id = ids[index]
                item = CartItem.objects.get(product=product, id=id)
                item.quantity += 1
                item.save()
            else:
                # create a new variation in cart
                item = CartItem.objects.create(product=product, user=current_user, quantity=1)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product=product,
                user=current_user,
                quantity=1,
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect('cart')
    else:
        product_variation = []
        if request.method == "POST":
            for i in request.POST:
                key = i
                value = request.POST[key]
                try:
                    variation_ = VariationModel.objects.get(product=product, variation_category__iexact=key,
                                                            variation_value__iexact=value)
                    product_variation.append(variation_)
                except:
                    pass
        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id=_cart_id(request)
            )
        cart.save()

        is_cart_item_exists = CartItem.objects.filter(cart=cart, product=product).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, cart=cart)
            existing_variation_list = []
            ids = []
            for i in cart_item:
                existing_variations = i.variations.all()
                existing_variation_list.append(list(existing_variations))
                ids.append(i.id)
            if product_variation in existing_variation_list:
                # increase the counter
                index = existing_variation_list.index(product_variation)
                id = ids[index]
                item = CartItem.objects.get(product=product, id=id)
                item.quantity += 1
                item.save()
            else:
                # create a new variation in cart
                item = CartItem.objects.create(product=product, cart=cart, quantity=1)
                if len(product_variation) > 0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
        else:
            cart_item = CartItem.objects.create(
                product=product,
                cart=cart,
                quantity=1,
            )
            if len(product_variation) > 0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
        return redirect('cart')


def remove_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(user=request.user, product=product, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(cart=cart, product=product, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')


def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(user=request.user, product=product, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(cart=cart, product=product, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')


def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for item in cart_items:
            total += (item.product.price) * item.quantity
            quantity += item.quantity
        tax = int(total * (2.25 / 100))
        grand_total = int(tax + total)
    except ObjectDoesNotExist:
        pass
    data = dict(
        total=total,
        quantity=quantity,
        cart_items=cart_items,
        tax=tax,
        grand_total=grand_total,
    )
    return render(request, 'store/cart.html', data)


@login_required(login_url='signin')
def checkout(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for item in cart_items:
            total += (item.product.price) * item.quantity
            quantity += item.quantity
        tax = int(total * (2.25 / 100))
        grand_total = int(tax + total)
    except ObjectDoesNotExist:
        pass
    data = dict(
        total=total,
        quantity=quantity,
        cart_items=cart_items,
        tax=tax,
        grand_total=grand_total,
    )
    return render(request, "store/checkout_main.html", data)
