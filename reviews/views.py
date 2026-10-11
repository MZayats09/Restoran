from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect

from menu.models import Dish

from .forms import ReviewForm
from .models import Review


@login_required
def add_review(request, slug):
    dish = get_object_or_404(Dish, slug=slug)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review, created = Review.objects.update_or_create(
                dish=dish, user=request.user,
                defaults={'rating': form.cleaned_data['rating'], 'text': form.cleaned_data['text']},
            )
            messages.success(request, 'Дякуємо за відгук!')
    return redirect('menu:dish_detail', slug=slug)


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if not (request.user.profile.is_admin_role or review.user == request.user):
        messages.error(request, 'Недостатньо прав для видалення цього відгуку.')
        return redirect('menu:dish_detail', slug=review.dish.slug)
    slug = review.dish.slug
    review.delete()
    messages.success(request, 'Відгук видалено.')
    return redirect('menu:dish_detail', slug=slug)
