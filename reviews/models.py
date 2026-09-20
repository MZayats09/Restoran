from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from menu.models import Dish


class Review(models.Model):
    dish = models.ForeignKey(Dish, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    text = models.TextField(blank=True, verbose_name='Відгук')
    is_approved = models.BooleanField(default=True, verbose_name='Схвалено (не приховано)')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('dish', 'user')
        verbose_name = 'Відгук'
        verbose_name_plural = 'Відгуки'

    def __str__(self):
        return f'{self.user.username} → {self.dish.name} ({self.rating}★)'
