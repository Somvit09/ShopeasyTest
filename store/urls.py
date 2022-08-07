from django.urls import path
from . import views

urlpatterns = [
    path('', views.storeHome, name='store'),
    path('category/<slug:category_slug>/', views.storeHome, name='product_by_categories'),
    path('category/<slug:category_slug>/<slug:product_slug>/', views.product_details, name='product_details'),
    path('search/', views.search, name='search'),
    path('submit_review/<int:product_id>/', views.submit_review, name='submit_review'),
]