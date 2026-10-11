from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Category, Dish


def menu_list(request):
    query = request.GET.get('q', '').strip()
    category_slug = request.GET.get('category', '')

    dishes = Dish.objects.select_related('category').all()
    if query:
        dishes = dishes.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if category_slug:
        dishes = dishes.filter(category__slug=category_slug)

    categories = Category.objects.all()
    return render(request, 'menu/menu_list.html', {
        'dishes': dishes,
        'categories': categories,
        'query': query,
        'selected_category': category_slug,
    })


def dish_detail(request, slug):
    dish = get_object_or_404(Dish.objects.select_related('category'), slug=slug)
    reviews = dish.reviews.select_related('user').order_by('-created_at')
    return render(request, 'menu/dish_detail.html', {'dish': dish, 'reviews': reviews})
