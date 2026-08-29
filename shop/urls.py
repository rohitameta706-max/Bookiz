from django.urls import path
from . import views
urlpatterns = [
    path("",views.StartingPageView.as_view(),name="starting-page"),
    path("books/",views.AllBookView.as_view(),name="all-books-page"),
    path("posts/<slug:slug>/",views.BookDetailView.as_view(),name="book-detail-page"),
    path("cart/add/<slug:slug>/",views.AddToCartView.as_view(),name="add-to-cart"),
    path("cart/",views.CartView.as_view(),name="cart-page"),
    path("cart/increase/<int:book_id>/",views.increase_cart,name="increase-cart"),
    path("cart/decrease/<int:book_id>/",views.decrease_cart,name="decrease-cart"),
    path("cart/remove/<int:book_id>/",views.remove_from_cart,name="remove-from-cart"),
    path("checkout/",views.checkout,name="checkout-page"),
    path("orders/",views.my_orders,name="orders-page"),
    path("success/",views.success,name="success"),
    path("subscribe/", views.subscribe_view, name="subscribe-success-page")
]