from django.shortcuts import render
from category.models import Category
from store.models import Product, ReviewRating


def home(request):
    products = Product.objects.all().filter(is_available=True).order_by('-created_date')
    categories = Category.objects.all()
    # getting all the reviews
    for product in products:
        reviews = ReviewRating.objects.filter(product_id=product.id, status=True)
    data = {
        'products': products,
        'categories': categories,
        'reviews': reviews,
    }
    return render(request, 'index.html', data)



