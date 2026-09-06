from datetime import date as date_cls

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView

from .cart import Cart
from .forms import RegisterForm, ReviewForm, CheckoutForm, BookingForm
from .models import Dish, RestaurantTable, Booking, Order, OrderItem, Review

TIME_SLOTS = ['12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00', '19:00', '20:00', '21:00']


# ---------- Головна ----------

def home(request):
    popular = Dish.objects.filter(available=True).order_by('-id')
    popular = sorted(popular, key=lambda d: (d.average_rating or 0), reverse=True)[:4]
    return render(request, 'home.html', {'popular': popular})


# ---------- Меню ----------

class MenuListView(ListView):
    model = Dish
    template_name = 'menu.html'
    context_object_name = 'dishes'

    def get_queryset(self):
        qs = Dish.objects.all()
        category = self.request.GET.get('category')
        q = self.request.GET.get('q')
        if category:
            qs = qs.filter(category=category)
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = Dish.CATEGORY_CHOICES
        ctx['selected_category'] = self.request.GET.get('category', '')
        ctx['query'] = self.request.GET.get('q', '')
        return ctx


class DishDetailView(DetailView):
    model = Dish
    template_name = 'dish_detail.html'
    context_object_name = 'dish'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['review_form'] = ReviewForm()
        ctx['reviews'] = self.object.reviews.select_related('user')
        return ctx

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not request.user.is_authenticated:
            messages.error(request, 'Увійди в профіль, щоб залишити відгук.')
            return redirect('login')
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.dish = self.object
            review.user = request.user
            review.save()
            messages.success(request, 'Дякуємо за відгук!')
            return redirect('dish_detail', pk=self.object.pk)
        ctx = self.get_context_data()
        ctx['review_form'] = form
        return render(request, self.template_name, ctx)


@login_required
def toggle_availability(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'Лише адміністратор може змінювати наявність страв.')
        return redirect('dish_detail', pk=pk)
    dish = get_object_or_404(Dish, pk=pk)
    dish.available = not dish.available
    dish.save()
    messages.success(request, f'«{dish.name}» тепер {"в наявності" if dish.available else "недоступна"}.')
    return redirect('dish_detail', pk=pk)


@login_required
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if not request.user.is_staff:
        messages.error(request, 'Лише адміністратор може видаляти відгуки.')
        return redirect('dish_detail', pk=review.dish_id)
    dish_id = review.dish_id
    review.delete()
    messages.success(request, 'Відгук видалено.')
    return redirect('dish_detail', pk=dish_id)


# ---------- Кошик ----------

def cart_view(request):
    cart = Cart(request)
    return render(request, 'cart.html', {'cart': cart, 'cart_total': cart.total_price()})


def cart_add(request, pk):
    dish = get_object_or_404(Dish, pk=pk)
    if not dish.available:
        messages.error(request, 'Ця страва зараз недоступна.')
        return redirect(request.META.get('HTTP_REFERER', 'menu'))
    Cart(request).add(dish)
    messages.success(request, f'«{dish.name}» додано в кошик.')
    return redirect(request.META.get('HTTP_REFERER', 'menu'))


def cart_update(request, pk):
    if request.method == 'POST':
        action = request.POST.get('action')
        cart = Cart(request)
        current = cart.cart.get(str(pk), 0)
        if action == 'increase':
            cart.set_quantity(pk, current + 1)
        elif action == 'decrease':
            cart.set_quantity(pk, current - 1)
    return redirect('cart')


def cart_remove(request, pk):
    Cart(request).remove(pk)
    return redirect('cart')


# ---------- Оформлення замовлення ----------

def checkout_view(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.info(request, 'Кошик порожній — спершу додай щось із меню.')
        return redirect('menu')

    initial = {}
    if request.user.is_authenticated:
        initial['name'] = request.user.get_full_name() or request.user.username

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user if request.user.is_authenticated else None
            order.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    dish=item['dish'],
                    dish_name=item['dish'].name,
                    price=item['dish'].price,
                    quantity=item['quantity'],
                )
            cart.clear()
            messages.success(request, 'Замовлення оформлено!')
            return redirect('order_history')
    else:
        form = CheckoutForm(initial=initial)

    return render(request, 'checkout.html', {'form': form, 'cart_total': cart.total_price()})


# ---------- Історія замовлень ----------

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).prefetch_related('items')
    return render(request, 'order_history.html', {'orders': orders})


@login_required
def order_reorder(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    cart = Cart(request)
    for item in order.items.all():
        if item.dish_id and item.dish.available:
            cart.add(item.dish, item.quantity)
    messages.success(request, 'Товари з попереднього замовлення додано в кошик.')
    return redirect('cart')


# ---------- Столики / бронювання ----------

def booking_map(request):
    selected_date = request.GET.get('date') or date_cls.today().isoformat()
    selected_time = request.GET.get('time') or '19:00'

    tables = list(RestaurantTable.objects.all())
    for t in tables:
        t.booked = t.bookings.filter(date=selected_date, time=selected_time).exists()
        t.marker_size = 34 + t.seats * 4

    if request.user.is_authenticated:
        my_bookings = Booking.objects.filter(user=request.user).select_related('table')
    else:
        my_bookings = Booking.objects.none()

    return render(request, 'booking.html', {
        'tables': tables,
        'selected_date': selected_date,
        'selected_time': selected_time,
        'time_slots': TIME_SLOTS,
        'my_bookings': my_bookings,
        'today': date_cls.today().isoformat(),
    })


def booking_create(request, pk):
    table = get_object_or_404(RestaurantTable, pk=pk)
    if request.method == 'POST':
        form = BookingForm(request.POST, table=table)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.table = table
            booking.user = request.user if request.user.is_authenticated else None
            booking.save()
            messages.success(request, f'Столик №{table.number} заброньовано на {booking.date} о {booking.time}.')
            return redirect('booking_map')
        else:
            for err in form.non_field_errors():
                messages.error(request, err)
            for field, errs in form.errors.items():
                if field != '__all__':
                    for e in errs:
                        messages.error(request, e)
    return redirect('booking_map')


@login_required
def booking_cancel(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if booking.user != request.user and not request.user.is_staff:
        messages.error(request, 'Це не твоє бронювання.')
        return redirect('booking_map')
    booking.delete()
    messages.success(request, 'Бронювання скасовано.')
    return redirect('booking_map')


# ---------- Реєстрація ----------

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Вітаємо, {user.username}! Акаунт створено.')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})
