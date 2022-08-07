from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


# Create your models here.
class MyAccountManager(BaseUserManager):
    def create_account(self, full_name, username, email, password=None):
        if not username:
            raise ValueError('user must have username')
        if not email:
            raise ValueError('Email is required')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
            full_name=full_name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, full_name, password):
        user = self.create_account(
            email=self.normalize_email(email),
            username=username,
            password=password,
            full_name=full_name,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superadmin = True
        user.is_active = True
        user.save(using=self._db)
        return user


class Accounts(AbstractBaseUser):
    full_name = models.CharField(max_length=150)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=150, unique=True)
    phone_number = models.CharField(max_length=50)

    # required field
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'username']

    class Meta:
        verbose_name = 'Accounts'
        verbose_name_plural = 'Accounts'

    objects = MyAccountManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, add_label):
        return True


class UserProfile(models.Model):
    user = models.OneToOneField(Accounts, on_delete=models.CASCADE)
    address_line_1 = models.CharField(max_length=350, blank=True)
    address_line_2 = models.CharField(max_length=350, blank=True)
    profile_picture = models.ImageField(blank=True, upload_to='user profile')
    country = models.CharField(max_length=150)
    state = models.CharField(max_length=150)
    city = models.CharField(max_length=150)

    def __str__(self):
        return self.user.full_name

    def full_addr(self):
        return f"{self.address_line_1} {self.address_line_2}"
