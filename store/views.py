from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, ProductGalleryModel
from category.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .forms import ReviewFrom
from .models import VariationModel, ReviewRating
from django.contrib import messages
from Order.models import Order, Order_product


# Create your views here.
def storeHome(request, category_slug=None):
    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=categories, is_available=True)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        product_count = products.count()
    paginator = Paginator(products, 3)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)
    data = {
        'products': paged_products,
        'product_count': product_count,
    }
    return render(request, 'store/store.html', data)


def product_details(request, category_slug=None, product_slug=None):
    try:
        single_product = Product.objects.get(category__slug=category_slug,
                                             slug=product_slug)  # __ to get the slug from the foreign model Category which is
        # from the category model by the category in Product model
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e
    if request.user.is_authenticated:
        try:
            order_product = Order_product.objects.filter(product_id=single_product.id, user=request.user).exists()
        except Order_product.DoesNotExist:
            order_product = None
    else:
        order_product = None

    # getting all the reviews
    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)
    # getting all the images of this product
    product_gallery = ProductGalleryModel.objects.filter(product_id=single_product.id)
    data = dict(
        single_product=single_product,
        in_cart=in_cart,
        order_product=order_product,
        reviews=reviews,
        product_gallery=product_gallery,
    )
    return render(request, 'store/product-detail.html', data)


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(
                Q(product_name__icontains=keyword.capitalize()) | Q(slug__icontains=keyword.capitalize()) |
                Q(category__slug__icontains=keyword.capitalize()) |
                Q(category__category_name__icontains=keyword.capitalize()))
            product_count = products.count()  # product_name__icontains means it will search keyword in the product name of Product model
    data = dict(products=products, product_count=product_count)
    return render(request, 'store/search-result.html', data)


def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == "POST":
        try:
            review = ReviewRating.objects.get(user__id=request.user.id,
                                              product__id=product_id)  # __ means  the id of the Accounts model of
            # user foreignkey
            form = ReviewFrom(request.POST, instance=review) # update the review
            form.save()
            messages.success(request, "Thank you! You review has been updated.")
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewFrom(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)