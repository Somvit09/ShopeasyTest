from django.contrib import admin
from .models import Product, VariationModel, ReviewRating, ProductGalleryModel
import admin_thumbnails


# Register your models here.

@admin_thumbnails.thumbnail('image')
class ProductGalleryModelAdmin(admin.TabularInline):
    model = ProductGalleryModel
    extra = 1


class ModelAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'modified_date', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}
    inlines = [ProductGalleryModelAdmin]


class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active',)
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'variation_value', 'is_active',)


admin.site.register(Product, ModelAdmin)
admin.site.register(VariationModel, VariationAdmin)
admin.site.register(ReviewRating)
admin.site.register(ProductGalleryModel)
