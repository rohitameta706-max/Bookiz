from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from django.urls import reverse
from django.views.generic import View, ListView, DetailView
from django.db.models import Q
from decimal import Decimal
from django.contrib import messages
from django.db import transaction
from .models import Book, Order, OrderItem, User, Subscribers

def get_date(book):
    return book["created_at"]

class StartingPageView(ListView):
    template_name = "shops/home.html"
    model = Book
    ordering = ["-created_at"]
    context_object_name = "books"
    def get_queryset(self):
        queryset = super().get_queryset()
        data = queryset[:8]
        return data
    
class AllBookView(ListView):
    template_name = "shops/all-books.html"
    model = Book
    ordering = ["-created_at"]
    context_object_name = "all_books"

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('q', '')
        selected_category = self.request.GET.get('category', '')
        
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | Q(author__icontains=search_query)
            )
        if selected_category:
            queryset = queryset.filter(category__name__iexact=selected_category)
        return queryset


class BookDetailView(DetailView):
    model = Book
    template_name = "shops/book-detail.html"
    context_object_name = "book"
    slug_field = "slug"      
    slug_url_kwarg = "slug" 


def add_to_cart(request, slug):
    book = get_object_or_404(Book, slug=slug)
    cart = request.session.get('cart', {})
    if str(book.id) in cart:
        cart[str(book.id)]['quantity'] += 1
    else:
        cart[str(book.id)] = {
            'title': book.title,
            'price': float(book.price),
            'quantity': 1,
            'image': book.images.url if book.images else ''
        }
    request.session['cart'] = cart
    return redirect('cart-page')


#for designing the page first. Used dummy data and their views.Then made class-based views
# def starting_page(request):
#     return render(request, "shops/home.html", {
#         "books": books 
#     })

# def book_detail(request, slug):
#     identified_book = next(
#         (book for book in books if book["slug"] == slug), None
#     )
#     if identified_book is None:
#         raise Http404("Book not found")
#     return render(
#         request,
#         "shops/book-detail.html",
#         {
#             "book": identified_book,
#         },
#     )

# def allbooks(request):
#     search_query = request.GET.get('q', '')
#     selected_category = request.GET.get('category', '')
#     filtered_books = books
#     if search_query:
#         filtered_books = [
#             book for book in filtered_books 
#             if search_query.lower() in book['title'].lower() or search_query.lower() in book['author'].lower()
#         ]
#     if selected_category:
#         filtered_books = [
#             book for book in filtered_books 
#             if book['category'].lower() == selected_category.lower()
#         ]
#     return render(request, "shops/all-books.html", {
#         "all_books": filtered_books
#     })

# def cart_page(request):
#     return render(request, "shops/cart.html", {
#         "cart_items": cart_items,
#         "cart_total": cart_total
#     })

def success(request):
    return render(request, "shops/success.html")


class AddToCartView(View):
    def post(self, request, slug):
        book = get_object_or_404(Book, slug=slug)
        cart = request.session.get("cart", {})
        book_id = str(book.id)
        quantity = cart.get(book_id, 0)
        if quantity >= book.stock:
            messages.error(request, "Not enough stock available.")
            return redirect("cart-page")
        cart[book_id] = quantity + 1
        request.session["cart"] = cart
        request.session.modified = True
        messages.success(request, "Book added to cart.")
        return redirect("cart-page")


class CartView(View):
    def get(self, request):
        cart = request.session.get("cart", {})
        cart_items = []
        cart_total = Decimal("0")
        for book_id, quantity in cart.items():
            book = Book.objects.get(id=book_id)
            total = book.price * quantity
            cart_items.append({
                "book": book,
                "quantity": quantity,
                "total_price": total,
            })
            cart_total += total
        return render(
            request,
            "shops/cart.html",
            {
                "cart_items": cart_items,
                "cart_total": cart_total,
            }
        )


def increase_cart(request, book_id):
    cart = request.session.get("cart", {})
    book = get_object_or_404(Book, id=book_id)
    key = str(book_id)
    if cart.get(key, 0) < book.stock:
        cart[key] = cart.get(key, 0) + 1
    request.session["cart"] = cart
    return redirect("cart-page")


def decrease_cart(request, book_id):
    cart = request.session.get("cart", {})
    key = str(book_id)
    if key in cart:
        cart[key] -= 1
        if cart[key] <= 0:
            del cart[key]
    request.session["cart"] = cart
    return redirect("cart-page")


def remove_from_cart(request, book_id):
    cart = request.session.get("cart", {})
    cart.pop(str(book_id), None)
    request.session["cart"] = cart
    return redirect("cart-page")


def my_orders(request):
    user_id = request.session.get("user_id")
    orders = Order.objects.none()
    if user_id:
        orders = Order.objects.filter(user_id=user_id).prefetch_related("items__book").order_by("-created_at")
    return render(
        request,
        "shops/my-order.html",{
            "orders": orders
        }
    )

def category(request):
    books = Book.objects.all()
    search_query = request.GET.get('q','').strip()
    selected_category = request.GET.get('category','').strip()
    if search_query:
        books = books.filter(Q(title__iscontains=search_query) | Q(author__iscontains = search_query))
    if selected_category:
        books = books.filter(category__isexact=selected_category)
    context={
        "all_books":books
    }
    return render(request, "shops/all-books.html", context)


def checkout(request):
    if request.method == "GET":
        return render(request, "shops/checkout.html")    
    name = request.POST.get("name")
    email = request.POST.get("email")
    address = request.POST.get("address")
    cart = request.session.get("cart", {})
    if not cart:
        return redirect("cart-page")
    with transaction.atomic():
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "name": name,
                "address": address,
            }
        )
        request.session["user_id"] = user.id
        total = Decimal("0")
        books_data = []
        for book_id, quantity in cart.items():
            book = Book.objects.select_for_update().get(id=book_id)
            if quantity > book.stock:
                messages.error(
                    request,
                    f"Only {book.stock} copies of {book.title} available."
                )
                return redirect("cart-page")
            total += book.price * quantity
            books_data.append((book, quantity))
        order = Order.objects.create(
            user=user,
            total_price=total,
            address=address
        )
        for book, quantity in books_data:
            OrderItem.objects.create(
                order=order,
                book=book,
                quantity=quantity,
                price=book.price)
            book.stock -= quantity
            book.save()
    request.session["cart"] = {}
    messages.success(request, "Order placed successfully!")
    return redirect("success")


def subscribe_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if email:
            if Subscribers.objects.filter(email=email).exists():
                messages.info(request, "You are already subscribed to the Bookiz Newsletter")
            else:
                Subscribers.objects.create(email=email)
                messages.success(request, "Thank You For joining the ChapterOne Readers club")
            return redirect(request.META.get('HTTP_REFERER', 'starting-page'))
    return redirect('starting-page')
