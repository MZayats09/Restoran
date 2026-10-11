from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from menu.models import Dish

from .cart import Cart


@require_POST
def cart_add(request, dish_id):
    cart = Cart(request)
    dish = get_object_or_404(Dish, id=dish_id, is_available=True)
    quantity = int(request.POST.get('quantity', 1))
    cart.add(dish=dish, quantity=quantity)
    return redirect('cart:cart_detail')


@require_POST
def cart_update(request, dish_id):
    cart = Cart(request)
    dish = get_object_or_404(Dish, id=dish_id)
    quantity = int(request.POST.get('quantity', 1))
    cart.add(dish=dish, quantity=quantity, override_quantity=True)
    return redirect('cart:cart_detail')


@require_POST
def cart_remove(request, dish_id):
    cart = Cart(request)
    dish = get_object_or_404(Dish, id=dish_id)
    cart.remove(dish)
    return redirect('cart:cart_detail')


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'cart/cart_detail.html', {'cart': cart})
