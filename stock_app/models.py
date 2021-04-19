from django.db import models
from re import compile


# Create your models here.
class UserManager(models.Manager):
    def basic_validation(self, post_data):
        email_regex = compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        errors = {}
        if len(post_data['first_name']) < 2:
            errors['first_name'] = "First Name must be 2 or more characters"
        if len(post_data['last_name']) < 2:
            errors['last_name'] = "Last Name must be 2 or more characters"
        if not email_regex.match(post_data['email_address']):
            errors['email_address'] = "Please enter a valid email address"
        if post_data['password'] != post_data['confirm_password']:
            errors['password'] = "Passwords do not match"
        if len(post_data['password']) < 8:
            errors['password'] = "Password must be 8 characters or longer"
        return errors


class StockManager(models.Manager):
    def basic_validation(self, post_data):
        pass


class User(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email_address = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    objects = UserManager()


#######
# Portfolio
class Portfolio(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='portfolio')
#######


#######
# Stock
class Stock(models.Model):
    ticker = models.CharField(max_length=5)
    after_ticker = models.CharField(max_length=2)
    price = models.DecimalField(max_digits=13, decimal_places=6)
    description = models.TextField()
    fifty_two_week_high = models.DecimalField(max_digits=13, decimal_places=6)
    fifty_two_week_low = models.DecimalField(max_digits=13, decimal_places=6)
    fifty_day_moving_average = models.DecimalField(max_digits=13, decimal_places=6)
    two_hundred_day_moving_average = models.DecimalField(max_digits=13, decimal_places=6)
    objects = StockManager()


class StockDay(models.Model):
    date = models.DateField()
    day_open = models.DecimalField(max_digits=13, decimal_places=6, blank=True, null=True)
    day_close = models.DecimalField(max_digits=13, decimal_places=6, blank=True, null=True)
    day_high = models.DecimalField(max_digits=13, decimal_places=6, blank=True, null=True)
    day_low = models.DecimalField(max_digits=13, decimal_places=6, blank=True, null=True)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='stock_days')


class OneMinuteSeries(models.Model):
    time = models.DateTimeField()
    price = models.DecimalField(max_digits=13, decimal_places=6)
    stock_day = models.ForeignKey(StockDay, on_delete=models.CASCADE, related_name='time_series_days')


class OwnedStock(models.Model):
    shares = models.IntegerField()
    purchase_date_time = models.DateTimeField()
    purchase_price = models.DecimalField(max_digits=13, decimal_places=6)
    sell_date_time = models.DateTimeField(blank=True, null=True)
    sell_price = models.DecimalField(max_digits=13, decimal_places=6, blank=True, null=True)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='owned_stocks')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_stocks')
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='owned_stocks')
#######


#######
# Bank
class Bank(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='banks')
    bank_name = models.CharField(max_length=255)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='banks')


class Investment(models.Model):
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name='investments')
    investment_amount = models.DecimalField(max_digits=13, decimal_places=6)
    investment_date = models.DateTimeField()
#######
