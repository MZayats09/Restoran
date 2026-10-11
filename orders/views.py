from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from cart.cart import Cart

from .forms import OrderCreateForm
from .models import Order, OrderItem


def order_create(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, 'Ваш кошик порожній.')
        return redirect('menu:menu_list')

    initial = {}
    if request.user.is_authenticated:
        initial['full_name'] = request.user.get_full_name() or request.user.username
        initial['phone'] = getattr(request.user.profile, 'phone', '')
        initial['address'] = getattr(request.user.profile, 'address', '')

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user
            order.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    dish=item['dish'],
                    price=item['price'],
                    quantity=item['quantity'],
                )
            cart.clear()
            messages.success(request, 'Замовлення успішно оформлено!')
            return redirect('orders:order_detail', order_id=order.id)
    else:
        form = OrderCreateForm(initial=initial)

    return render(request, 'orders/order_create.html', {'cart': cart, 'form': form})


@login_required
def order_detail(request, order_id):
    if request.user.profile.is_admin_role:
        order = get_object_or_404(Order, id=order_id)
    else:
        order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items__dish')
    return render(request, 'orders/order_history.html', {'orders': orders})


@login_required
def order_repeat(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    cart = Cart(request)
    for item in order.items.all():
        if item.dish.is_available:
            cart.add(dish=item.dish, quantity=item.quantity)
    messages.success(request, 'Страви із замовлення додано до кошика.')
    return redirect('cart:cart_detail')
