from django.shortcuts import render

from menu.models import Dish


def home(request):
    popular_dishes = Dish.objects.filter(is_popular=True, is_available=True)[:8]
    new_dishes = Dish.objects.filter(is_new=True, is_available=True)[:8]
    return render(request, 'core/home.html', {
        'popular_dishes': popular_dishes,
        'new_dishes': new_dishes,
    })
