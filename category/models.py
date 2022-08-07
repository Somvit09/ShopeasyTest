from django.db import models
from django.urls import reverse


# Create your models here.

class Category(models.Model):
    category_name = models.CharField(max_length=250, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    category_img = models.ImageField(upload_to='photos/categories', blank=True)
    description = models.TextField(max_length=350, blank=True)

    # for changing the plural form of Category in admin panel
    # this is the procedure
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def get_url(self):
        return reverse('product_by_categories', args=[self.slug])

    def __str__(self):
        return self.category_name
