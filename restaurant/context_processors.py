from .cart import Cart
from .models import Order


def cart_summary(request):
    cart = Cart(request)
    unread = 0
    if request.user.is_authenticated:
        unread = Order.objects.filter(user=request.user, status='ready', ready_notified=False).count()
    return {
        'cart_count': cart.total_quantity(),
        'unread_notifications': unread,
    }
