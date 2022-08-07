import django.utils.http
from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm, UserForm, UserProfileForm
from .models import Accounts, UserProfile
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth import logout
import requests

# email verification
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from carts.views import _cart_id
from carts.models import Cart, CartItem
from Order.models import Order, Order_product


# Create your views here.

def signin(request):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        # user = Accounts.objects.filter(email=email, password=password).exists()
        user = auth.authenticate(email=email, password=password)
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id=_cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                if is_cart_item_exists:
                    cart_item = CartItem.objects.filter(cart=cart)
                    # getting the variations
                    product_variation = []
                    for item in cart_item:
                        variation = item.variations.all()
                        product_variation.append(variation)

                    cart_item = CartItem.objects.filter(user=user)
                    existing_variation_list = []
                    ids = []
                    for i in cart_item:
                        existing_variations = i.variations.all()
                        existing_variation_list.append(list(existing_variations))
                        ids.append(i.id)

                    for i in product_variation:
                        if i in existing_variation_list:
                            index = existing_variation_list.index(i)
                            item_id = ids[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user = user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for j in cart_item:
                                j.user = user
                                j.save()
            except:
                pass
            auth.login(request, user)
            messages.success(request, "User Logged in Successfully")
            url = request.META.get('HTTP_REFERER')  # grab the previous url from path
            try:
                query = requests.utils.urlparse(url).query
                # the path from the query will be "next=/cart/checkout/" like this
                # now we have to do the path like a dictionary like {"next": "/cart/checkout/"}
                params = dict(x.split('=') for x in query.split('&'))
                if 'next' in params:
                    nextpage = params['next']
                    return redirect(nextpage)
            except:
                return redirect('dashboard')
        else:
            messages.error(request, "Invalid Credentials. Please Try Again.")
            return redirect('signin')

    return render(request, 'accounts/signin.html')


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            full_name = form.cleaned_data['full_name']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            confirm_password = form.cleaned_data['confirm_password']
            phone_number = form.cleaned_data['phone_number']
            username = form.cleaned_data['username']
            user = Accounts.objects.create_account(
                full_name=full_name,
                email=email,
                password=password,
                username=username,
            )
            user.phone_number = phone_number
            user.save()
            # email verification
            current_site = get_current_site(request)
            mail_subject = "Please activate your account."
            message = render_to_string('accounts/mail_message_verification.html', dict(
                user=user,
                domain=current_site,
                uid=urlsafe_base64_encode(force_bytes(user.pk)),
                token=default_token_generator.make_token(user),
            ))
            mail = email
            send_mail = EmailMessage(mail_subject, message, to=[mail, ])
            send_mail.send()
            # messages.success(request, 'An email was sent for verification. Kindly click on that link to activate your account.')
            return redirect('/accounts/signin/?command=verification&email=' + email)

    else:
        form = RegistrationForm()
    data = dict(
        form=form,
    )
    return render(request, 'accounts/register.html', data)


@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    messages.success(request, "You are successfully logged out.")
    return redirect('home')


def activate(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Accounts._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Accounts.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your account is successfully activated. Please login with credentials.")
        return redirect('signin')
    else:
        messages.error(request, "Invalid activation link.")
        return redirect('register')


@login_required(login_url='signin')
def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    order_count = orders.count()
    profile_picture = UserProfile.objects.get(user_id=request.user.id)
    data = dict(
        order_count=order_count,
        user_profile=profile_picture,
    )
    return render(request, 'accounts/dashboard.html', data)


@login_required(login_url='signin')
def my_orders(request):
    orders = Order.objects.order_by('-created_at').filter(user_id=request.user.id, is_ordered=True)
    data = dict(
        orders=orders,
    )
    return render(request, 'accounts/my_orders.html', data)


@login_required(login_url='signin')
def edit_profile(request):
    user_profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        user_profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if user_form.is_valid() and user_profile_form.is_valid():
            user_form.save()
            user_profile_form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        user_profile_form = UserProfileForm(instance=user_profile)
    data = dict(
        user_form=user_form,
        profile_form=user_profile_form,
        user_profile=user_profile,
    )
    return render(request, 'accounts/edit_profile.html', data)


@login_required(login_url='signin')
def change_password(request):
    if request.method == "POST":
        user_object = Accounts.objects.get(username__exact=request.user.username)
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
        if new_password == confirm_password:
            if user_object.check_password(current_password):
                user_object.set_password(new_password)
                user_object.save()
                messages.success(request, "Password has been changed successfully. Please login with new password")
                return redirect('signin')
            else:
                messages.error(request, "Password does not exist. Please retype your current password")
                return redirect('change_password')
        else:
            messages.error(request, "Password did not match. Please retype your new password.")
            return redirect('change_password')

    return render(request, 'accounts/change_password.html')


@login_required(login_url='signin')
def order_detail(request, order_id):
    order_details = Order_product.objects.filter(order__order_number=order_id)
    order = Order.objects.get(order_number=order_id)
    subtotal = order.order_total - order.tax
    data = dict(
        order_detail=order_details,
        order=order,
        subtotal=subtotal,
    )
    return render(request, 'accounts/order_detail.html', data)


def forgot_password(request):
    if request.method == "POST":
        email = request.POST['email']
        email_is_in_database = Accounts.objects.filter(email=email).exists()
        if email_is_in_database:
            user = Accounts.objects.get(email__exact=email)  # get that exact email from database

            # forgot password
            current_site = get_current_site(request)
            mail_subject = "Forgot Password"
            message = render_to_string('accounts/reset_password_link.html', dict(
                user=user,
                domain=current_site,
                uid=urlsafe_base64_encode(force_bytes(user.pk)),
                token=default_token_generator.make_token(user),
            ))
            mail = email
            send_mail = EmailMessage(mail_subject, message, to=[mail, ])
            send_mail.send()

            messages.success(request,
                             "Password reset link has been sent to your email address. Kindly reset password and login" +
                             " with new credentials.")
            return redirect('signin')
        else:
            messages.error(request, "Account does not exist.")
            return redirect('register')
    return render(request, 'accounts/forgot_password.html')


def reset_password_validation(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Accounts._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Accounts.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password.')
        return redirect('resetPassword')
    else:
        messages.error(request, "This link has expired.")
        return redirect('signin')


def resetPassword(request):
    if request.method == "POST":
        new_password = request.POST['new_password']
        retype_password = request.POST['retype_password']
        if new_password == retype_password:
            uid = request.session.get('uid')
            user = Accounts.objects.get(pk=uid)
            user.set_password(new_password)
            user.save()
            messages.success(request, 'Password has been changed.')
            return redirect('signin')
        else:
            messages.error(request, "You have typped wrong password. Please try again.")
            return redirect('resetPassword')
    else:
        return render(request, 'accounts/resetPassword.html')
