# Ресторанний додаток

Django-проєкт за ТЗ: онлайн-меню, кошик, оформлення замовлення з оплатою, історія
замовлень, відгуки та рейтинги з модерацією, а також карта залу з бронюванням
столиків.

## Стек

- Python 3.11+ / Django 5.x
- SQLite локально / Postgres на Render (перемикається автоматично через `DATABASE_URL`)
- Bootstrap 5 (через CDN) для фронтенду
- Django sessions для кошика гостя (без реєстрації)
- gunicorn + whitenoise — продакшн-сервер і роздача статики на Render

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
| **Карта залу з бронюванням**      | `RestaurantTable`, `Booking`, `booking.html` (SVG-карта) |
| **Кнопка переходу в адмін-панель**| Видима у навбарі для `is_staff` → `/admin/`     |
| **Сповіщення про готовність замовлення** | Черга менеджера → статус «Готово» → клієнту спливає тост |

## Як працює сповіщення про готовність

1. Менеджер (`is_staff=True`) відкриває **«Черга замовлень»** (кнопка в навбарі
   або `/manager/orders/`) і бачить активні замовлення.
2. Натискає **«✓ Готово»** — статус замовлення міняється на «Готове до
   видачі», а полю `ready_notified` виставляється `False`.
3. У браузері клієнта (лише для авторизованих користувачів) кожні 8 секунд
   виконується опитування `/notifications/check/`. Щойно знаходить готове
   непрочитане замовлення — показує спливаючий тост знизу екрана і оновлює
   бейдж дзвіночка 🔔 в навбарі, а сервер одразу позначає його як показане.
4. Далі менеджер натискає «Видано клієнту», щоб закрити замовлення.

Це реалізовано через звичайний polling (без WebSocket/Channels), тому працює
"з коробки" на будь-якому хостингу без додаткової інфраструктури.

## Деплой на Render

Проєкт уже підготовлено для Render — `render.yaml` описує і вебсервіс, і
безкоштовну Postgres-базу, тому майже нічого не потрібно вводити руками.

### Крок 1. Запуш код на GitHub

```bash
git push origin main      # або develop — обирай гілку, яку Render має деплоїти
```

### Крок 2. Створи Blueprint на Render

1. Зайди на [render.com](https://render.com) → **New** → **Blueprint**.
2. Підключи свій GitHub-репозиторій із цим проєктом.
3. Render сам знайде `render.yaml` у корені репозиторію і запропонує
   створити:
   - **restaurant-app** — веб-сервіс на Python (free-план);
   - **restaurant-db** — базу Postgres (free-план).
4. Натисни **Apply**. Render сам:
   - згенерує випадковий `SECRET_KEY`;
   - з'єднає `DATABASE_URL` сервісу з базою `restaurant-db`;
   - виконає `build.sh` (встановлення залежностей, `collectstatic`, `migrate`);
   - запустить сайт через `gunicorn config.wsgi:application`.

Деплой триває кілька хвилин. Коли статус стане **Live**, сайт буде доступний
за адресою вигляду `https://restaurant-app-XXXX.onrender.com`.

### Крок 3. Наповни базу даними (один раз)

Відкрий сервіс на Render → вкладка **Shell** → виконай:

```bash
python manage.py seed_data
python manage.py createsuperuser
```

Це створить демо-страви, столики, тестового користувача `guest/guest12345`
і твій акаунт адміністратора для `/admin/`.

### Якщо потрібно змінити домен / дозволені хости

Безкоштовний домен `*.onrender.com` Render додає в `ALLOWED_HOSTS`
автоматично (через змінну `RENDER_EXTERNAL_HOSTNAME`, яку Render сам
проставляє). Якщо згодом підключиш власний домен — додай його в змінну
середовища `ALLOWED_HOSTS` на сторінці сервісу (**Environment** →
**Environment Variables**), через кому з рештою хостів, і в
`CSRF_TRUSTED_ORIGINS` (повний URL з `https://`).

### Обмеження безкоштовного плану

- Безкоштовний веб-сервіс засинає після ~15 хв без запитів і "прокидається"
  на наступний запит за кілька секунд — це нормально для демо/навчального
  проєкту.
- Безкоштовна Postgres-база на Render видаляється через 90 днів простою
  бездіяльності — якщо проєкт довгостроковий, вчасно перейди на платний
  план бази.

## GitFlow

Репозиторій ініціалізовано з гілками `main` і `develop`. Нові функції
розробляй у гілках `feature/назва-фічі` від `develop`, зливай через Pull
Request, а в `main` потрапляють лише готові релізи.
