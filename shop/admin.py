from django.contrib import admin
from .models import User, Category, Book, Order, OrderItem, Subscribers
# Register your models here.

class BookAdmin(admin.ModelAdmin):
    list_filter = ("author","created_at")
    prepopulated_fields = {"slug":("title",)}

admin.site.register(User)
admin.site.register(Category)
admin.site.register(Book,BookAdmin)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Subscribers)