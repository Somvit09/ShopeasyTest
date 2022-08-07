from django.db import models
from accounts.models import Accounts
from store.models import Product, VariationModel


# Create your models here.

class Payment(models.Model):
    user = models.ForeignKey(Accounts, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=250)
    amount_paid = models.CharField(max_length=100)
    status = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_id


dropdown_choices = (
    ("New", "New"),
    ("Accepted", "Accepted"),
    ("Completed", "Completed"),
    ("Canceled", "Canceled"),
)


class Order(models.Model):
    user = models.ForeignKey(Accounts, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    order_number = models.CharField(max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=150)
    email = models.EmailField(max_length=250)
    address_line_1 = models.CharField(max_length=350)
    address_line_2 = models.CharField(max_length=350, blank=True)
    country = models.CharField(max_length=150)
    state = models.CharField(max_length=150)
    city = models.CharField(max_length=150)
    order_total = models.FloatField()
    tax = models.FloatField()
    status = models.CharField(choices=dropdown_choices, max_length=15, default="New")
    ip = models.CharField(max_length=250, blank=True)
    order_note = models.CharField(max_length=350, blank=True)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def full_address(self):
        return f"{self.address_line_1} {self.address_line_2}"

    def state_country_info(self):
        return f"{self.city}, {self.state}, {self.country}"

    def __str__(self):
        return self.first_name


class Order_product(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(Accounts, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variations = models.ManyToManyField(VariationModel, blank=True)
    quantity = models.IntegerField()
    product_price = models.FloatField()
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.product_name
