from django.conf import settings
from django.db import models


class Table(models.Model):
    """Столик у залі ресторану. x, y — координати у відсотках (0-100) для відображення на карті."""
    number = models.PositiveIntegerField(unique=True, verbose_name='Номер столика')
    seats = models.PositiveIntegerField(default=2, verbose_name='К-сть місць')
    pos_x = models.FloatField(default=50, verbose_name='Позиція X (%)')
    pos_y = models.FloatField(default=50, verbose_name='Позиція Y (%)')
    is_active = models.BooleanField(default=True, verbose_name='Активний (доступний для бронювання)')

    class Meta:
        ordering = ['number']
        verbose_name = 'Столик'
        verbose_name_plural = 'Столики'

    def __str__(self):
        return f'Столик №{self.number} ({self.seats} місць)'

    def is_occupied_on(self, date, time_slot):
        return self.reservations.filter(date=date, time_slot=time_slot, status='confirmed').exists()


class Reservation(models.Model):
    TIME_SLOTS = [
        ('12:00', '12:00'), ('13:00', '13:00'), ('14:00', '14:00'),
        ('15:00', '15:00'), ('16:00', '16:00'), ('17:00', '17:00'),
        ('18:00', '18:00'), ('19:00', '19:00'), ('20:00', '20:00'),
        ('21:00', '21:00'), ('22:00', '22:00'),
    ]
    STATUS_CHOICES = [
        ('confirmed', 'Підтверджено'),
        ('cancelled', 'Скасовано'),
    ]

    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='reservations')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservations', null=True, blank=True
    )
    full_name = models.CharField(max_length=150, verbose_name="Ім'я та прізвище")
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    guests = models.PositiveIntegerField(default=2, verbose_name='К-сть гостей')
    date = models.DateField(verbose_name='Дата')
    time_slot = models.CharField(max_length=5, choices=TIME_SLOTS, verbose_name='Час')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    comment = models.TextField(blank=True, verbose_name='Коментар')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', 'time_slot']
        verbose_name = 'Бронювання'
        verbose_name_plural = 'Бронювання'

    def __str__(self):
        return f'Столик №{self.table.number} — {self.date} {self.time_slot}'
