from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from menu.models import Category, Dish
from reservations.models import Table


class Command(BaseCommand):
    help = 'Наповнює базу демо-даними (категорії, страви, столики, адмін)'

    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser('admin', 'admin@example.com', 'admin12345')
            admin.profile.role = 'admin'
            admin.profile.save()
            self.stdout.write(self.style.SUCCESS('Створено адміністратора: admin / admin12345'))

        categories = {
            'salads': 'Салати',
            'main': 'Основні страви',
            'desserts': 'Десерти',
            'drinks': 'Напої',
        }
        cats = {}
        for slug, name in categories.items():
            cat, _ = Category.objects.get_or_create(slug=slug, defaults={'name': name})
            cats[slug] = cat

        dishes = [
            ('salads', 'Цезар з куркою', 'cezar-z-kurkoyu', 145, 'Хрусткий салат з куркою, пармезаном та соусом цезар.', True, False),
            ('salads', 'Грецький салат', 'grecky-salat', 120, 'Свіжі овочі, сир фета та маслини з оливковою олією.', False, True),
            ('main', 'Стейк з телятини', 'steik-z-telyatyny', 320, 'Соковитий стейк середньої прожарки з овочами гриль.', True, False),
            ('main', 'Паста Карбонара', 'pasta-karbonara', 175, 'Класична паста з беконом, вершками та пармезаном.', True, False),
            ('main', 'Піца Маргарита', 'pizza-margarita', 165, 'Томатний соус, моцарела та базилік.', False, False),
            ('desserts', 'Тірамісу', 'tiramisu', 95, 'Ніжний італійський десерт з кавою та маскарпоне.', False, True),
            ('desserts', 'Чізкейк Нью-Йорк', 'chizkeik-new-york', 110, 'Класичний вершковий чізкейк.', False, False),
            ('drinks', 'Лимонад домашній', 'lemonade-domashniy', 65, 'Освіжаючий лимонад з м’ятою.', False, True),
            ('drinks', 'Кава американо', 'kava-americano', 45, 'Класична чорна кава.', False, False),
        ]
        for slug, name, dish_slug, price, desc, popular, new in dishes:
            Dish.objects.get_or_create(
                slug=dish_slug,
                defaults=dict(
                    category=cats[slug], name=name, description=desc,
                    price=price, is_available=True, is_popular=popular, is_new=new,
                ),
            )

        # Розстановка столиків у залі (сітка з відхиленнями, у %)
        layout = [
            (1, 2, 15, 20), (2, 2, 35, 20), (3, 4, 55, 18), (4, 4, 78, 22),
            (5, 2, 15, 45), (6, 6, 40, 48), (7, 2, 65, 45), (8, 4, 85, 50),
            (9, 4, 20, 75), (10, 2, 45, 78), (11, 6, 68, 75), (12, 2, 88, 78),
        ]
        for number, seats, x, y in layout:
            Table.objects.get_or_create(number=number, defaults={'seats': seats, 'pos_x': x, 'pos_y': y})

        self.stdout.write(self.style.SUCCESS('Демо-дані успішно додано.'))
