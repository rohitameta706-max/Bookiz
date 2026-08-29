from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class User(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField()
    email = models.EmailField()
    def __str__(self):
        return f"User is {self.name}"

class Category(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name
    
class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    description = models.TextField()
    slug = models.SlugField(unique=True)
    price = models.DecimalField(max_digits=8,decimal_places=2)
    images = models.ImageField(upload_to="books/")
    category = models.ForeignKey(Category,on_delete=models.CASCADE,related_name="books")
    stock = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.00, validators=[MinValueValidator(1.00), MaxValueValidator(5.00)])
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.title
    
class Order(models.Model):
    STATUS_CHOICES = [
        ("Processing","Processing"),
        ("Shipped", "Shipped"),
        ("Delivered","Delivered")
    ]
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10,decimal_places=2)
    address = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES,default="Processing")
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Order {self.id}"
    
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )
    book = models.ForeignKey(Book, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)

class Subscribers(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.email