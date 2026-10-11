from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Назва')
    slug = models.SlugField(max_length=100, unique=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'

    def __str__(self):
        return self.name


class Dish(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='dishes', verbose_name='Категорія')
    name = models.CharField(max_length=150, verbose_name='Назва')
    slug = models.SlugField(max_length=170, unique=True)
    description = models.TextField(blank=True, verbose_name='Опис')
    ingredients = models.TextField(blank=True, verbose_name='Інгредієнти')
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Ціна')
    image = models.ImageField(upload_to='dishes/', blank=True, null=True, verbose_name='Фото')
    is_available = models.BooleanField(default=True, verbose_name='В наявності')
    is_popular = models.BooleanField(default=False, verbose_name='Популярна страва')
    is_new = models.BooleanField(default=False, verbose_name='Нова пропозиція')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Страва'
        verbose_name_plural = 'Страви'

    def __str__(self):
        return self.name

    @property
    def average_rating(self):
        agg = self.reviews.aggregate(avg=models.Avg('rating'))
        return round(agg['avg'], 1) if agg['avg'] else None
