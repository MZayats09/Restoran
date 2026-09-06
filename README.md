# Ресторанний додаток

Django-проєкт за ТЗ: онлайн-меню, кошик, оформлення замовлення з оплатою, історія
замовлень, відгуки та рейтинги з модерацією, а також карта залу з бронюванням
столиків.

## Стек

- Python 3.11+ / Django 5.x
- SQLite (за замовчуванням, без додаткового налаштування)
- Bootstrap 5 (через CDN) для фронтенду
- Django sessions для кошика гостя (без реєстрації)

## Запуск локально

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate
python manage.py seed_data      # наповнює базу стравами, столиками й тестовим юзером
python manage.py createsuperuser   # свій акаунт адміністратора

python manage.py runserver
```

Відкрий http://127.0.0.1:8000/

- Тестовий користувач після `seed_data`: **guest / guest12345**
- Адміністратор — це суперюзер (`is_staff=True`), якого ти створив
  через `createsuperuser`, або будь-який користувач, якому в
  `/admin/` виставили галочку "Staff status".
- Django-адмінка (повне управління стравами, столиками, замовленнями,
  модерація відгуків): http://127.0.0.1:8000/admin/

## Відкриття в PyCharm

1. File → Open... → обери цю папку (`restaurant_app`).
2. PyCharm запропонує створити віртуальне середовище — обери
   інтерпретатор `venv/bin/python` (або створи новий через
   Settings → Project → Python Interpreter → Add → Virtualenv).
3. У терміналі PyCharm виконай команди зі списку вище
   (`pip install`, `migrate`, `seed_data`, `runserver`).
4. Для зручного дебагу онови Run/Debug Configuration:
   Script path → `manage.py`, Parameters → `runserver`.

## Структура проєкту

```
restaurant_app/
├── manage.py
├── config/            # налаштування проєкту (settings, urls, wsgi/asgi)
├── restaurant/         # основний застосунок
│   ├── models.py       # Dish, Review, RestaurantTable, Booking, Order, OrderItem
│   ├── views.py        # усі view'и (FBV + CBV)
│   ├── forms.py
│   ├── cart.py          # кошик на основі Django sessions
│   ├── admin.py
│   └── management/commands/seed_data.py
├── templates/           # HTML-шаблони (Bootstrap 5)
└── static/css/style.css # кастомна кольорова палітра
```

## Де що шукати відносно ТЗ

| Вимога ТЗ                        | Реалізація                                    |
|-----------------------------------|------------------------------------------------|
| Головна сторінка, пошук           | `views.home`, `menu.html` (GET `?q=`)           |
| Реєстрація / вхід, 2 ролі         | `django.contrib.auth` + `is_staff` як адмін     |
| Меню з категоріями, наявність     | `Dish`, `MenuListView`                          |
| Кошик                             | `restaurant/cart.py` (сесії Django)             |
| Оформлення замовлення, оплата     | `Order`, `checkout_view`                        |
| Історія замовлень / повтор        | `order_history`, `order_reorder`                |
| Відгуки й модерація адміном       | `Review`, `delete_review`, Django-адмінка       |
| **Карта залу з бронюванням**      | `RestaurantTable`, `Booking`, `booking.html`    |

## GitFlow

Репозиторій ініціалізовано з гілками `main` і `develop`. Нові функції
розробляй у гілках `feature/назва-фічі` від `develop`, зливай через Pull
Request, а в `main` потрапляють лише готові релізи.
