from django.db import models
from store.models import Product, VariationModel
from accounts.models import Accounts


# Create your models here.

class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    # for changing the plural form of Category in admin panel
    # this is the procedure
    class Meta:
        verbose_name = 'Cart'
        verbose_name_plural = 'Cart'

    def __str__(self):
        return self.cart_id


class CartItem(models.Model):
    user = models.ForeignKey(Accounts, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(VariationModel, blank=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, null=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    # for changing the plural form of Category in admin panel
    # this is the procedure
    class Meta:
        verbose_name = 'CartItem'
        verbose_name_plural = 'Cartitems'

    def sub_total(self):
        return self.product.price * self.quantity

    def __unicode__(self):
        return self.product
