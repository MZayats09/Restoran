from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse


class Dish(models.Model):
    CATEGORY_CHOICES = [
        ('salad', 'Салати'),
        ('main', 'Основні страви'),
        ('dessert', 'Десерти'),
        ('drink', 'Напої'),
    ]

    name = models.CharField('Назва', max_length=200)
    category = models.CharField('Категорія', max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField('Опис', blank=True)
    ingredients = models.TextField('Інгредієнти', blank=True)
    price = models.DecimalField('Ціна, ₴', max_digits=8, decimal_places=2)
    photo_url = models.URLField('Посилання на фото', blank=True)
    available = models.BooleanField('В наявності', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Страва'
        verbose_name_plural = 'Страви'
        ordering = ['category', 'name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('dish_detail', args=[self.pk])

    @property
    def average_rating(self):
        agg = self.reviews.aggregate(models.Avg('rating'))['rating__avg']
        return round(agg, 1) if agg else None

    @property
    def review_count(self):
        return self.reviews.count()


class Review(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(
        'Оцінка', validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    text = models.TextField('Текст відгуку')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Відгук'
        verbose_name_plural = 'Відгуки'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} → {self.dish} ({self.rating}★)'


class RestaurantTable(models.Model):
    number = models.PositiveIntegerField('Номер столика', unique=True)
    seats = models.PositiveIntegerField('Кількість місць')
    is_vip = models.BooleanField('VIP-зона', default=False)
    is_terrace = models.BooleanField('Тераса', default=False)
    pos_x = models.FloatField('Позиція X, %', default=50)
    pos_y = models.FloatField('Позиція Y, %', default=50)

    class Meta:
        verbose_name = 'Столик'
        verbose_name_plural = 'Столики'
        ordering = ['number']

    def __str__(self):
        return f'Столик №{self.number} ({self.seats} місць)'

    def is_booked_at(self, date, time):
        return self.bookings.filter(date=date, time=time).exists()


class Booking(models.Model):
    table = models.ForeignKey(RestaurantTable, on_delete=models.CASCADE, related_name='bookings')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    name = models.CharField('Ім\u2019я', max_length=120)
    phone = models.CharField('Телефон', max_length=30)
    date = models.DateField('Дата')
    time = models.TimeField('Час')
    guests = models.PositiveIntegerField('Кількість гостей')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Бронювання'
        verbose_name_plural = 'Бронювання'
        ordering = ['date', 'time']
        constraints = [
            models.UniqueConstraint(fields=['table', 'date', 'time'], name='unique_table_slot')
        ]

    def __str__(self):
        return f'Столик №{self.table.number} · {self.date} {self.time}'


class Order(models.Model):
    PAYMENT_CHOICES = [
        ('cash', 'Готівка при отриманні'),
        ('online', 'Онлайн-оплата'),
    ]
    STATUS_CHOICES = [
        ('new', 'Прийнято'),
        ('confirmed', 'Готується'),
        ('done', 'Виконано'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    name = models.CharField('Ім\u2019я та прізвище', max_length=150)
    phone = models.CharField('Телефон', max_length=30)
    address = models.CharField('Адреса доставки', max_length=255)
    payment_method = models.CharField('Спосіб оплати', max_length=10, choices=PAYMENT_CHOICES)
    status = models.CharField('Статус', max_length=15, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Замовлення'
        verbose_name_plural = 'Замовлення'
        ordering = ['-created_at']

    def __str__(self):
        return f'Замовлення №{self.pk} ({self.name})'

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    dish = models.ForeignKey(Dish, on_delete=models.SET_NULL, null=True, related_name='order_items')
    dish_name = models.CharField(max_length=200)  # snapshot in case a dish is later renamed/removed
    price = models.DecimalField(max_digits=8, decimal_places=2)  # snapshot price at order time
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Позиція замовлення'
        verbose_name_plural = 'Позиції замовлення'

    def __str__(self):
        return f'{self.quantity} × {self.dish_name}'

    @property
    def subtotal(self):
        return self.price * self.quantity
