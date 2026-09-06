from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from restaurant.models import Dish, RestaurantTable, Review

DISHES = [
    dict(name='Салат «Грецький»', category='salad', price=145,
         description='Класика середземномор\u2019я з хрусткими овочами та солоною фетою.',
         ingredients='Помідори, огірки, фета, оливки, червона цибуля, оливкова олія',
         photo_url='https://picsum.photos/seed/greek-salad/480/340'),
    dict(name='Буряковий салат з горіхами', category='salad', price=135,
         description='Печений буряк, козячий сир і волоські горіхи під медово-гірчичною заправкою.',
         ingredients='Буряк, волоські горіхи, козячий сир, мед, гірчиця',
         photo_url='https://picsum.photos/seed/beet-salad/480/340'),
    dict(name='Цезар з куркою', category='salad', price=165,
         description='Ромен, соковита куряча грудка, пармезан і домашні грінки.',
         ingredients='Салат ромен, куряче філе, пармезан, грінки, соус цезар',
         photo_url='https://picsum.photos/seed/caesar/480/340'),

    dict(name='Борщ український', category='main', price=120,
         description='Наваристий борщ на яловичині з часниковими пампушками.',
         ingredients='Буряк, капуста, яловичина, квасоля, пампушки з часником',
         photo_url='https://picsum.photos/seed/borsch/480/340'),
    dict(name='Деруни зі сметаною', category='main', price=110,
         description='Хрусткі картопляні деруни, подаються з домашньою сметаною.',
         ingredients='Картопля, цибуля, яйце, сметана',
         photo_url='https://picsum.photos/seed/deruny/480/340'),
    dict(name='Стейк з лосося на грилі', category='main', price=320, available=False,
         description='Лосось на грилі з овочами та кропово-лимонним соусом.',
         ingredients='Лосось, овочі гриль, кріп, лимон',
         photo_url='https://picsum.photos/seed/salmon-steak/480/340'),
    dict(name='Вареники з картоплею і грибами', category='main', price=130,
         description='Домашні вареники з підсмаженою цибулею.',
         ingredients='Тісто, картопля, гриби, смажена цибуля',
         photo_url='https://picsum.photos/seed/varenyky/480/340'),

    dict(name='Медовик', category='dessert', price=95,
         description='Ніжні медові коржі з кремом із сметани.',
         ingredients='Мед, борошно, сметанний крем',
         photo_url='https://picsum.photos/seed/medovyk/480/340'),
    dict(name='Чізкейк «Нью-Йорк»', category='dessert', price=110,
         description='Класичний вершковий чізкейк на пісочній основі.',
         ingredients='Вершковий сир, пісочна основа, ванільний соус',
         photo_url='https://picsum.photos/seed/cheesecake/480/340'),
    dict(name='Сирники з ягодами', category='dessert', price=90,
         description='Пухкі сирники з сезонними ягодами та медом.',
         ingredients='Сир кисломолочний, ягоди, мед',
         photo_url='https://picsum.photos/seed/syrnyky/480/340'),

    dict(name='Узвар домашній', category='drink', price=55,
         description='Компот із сушених яблук і груш за бабусиним рецептом.',
         ingredients='Сушені яблука, груші, чорнослив',
         photo_url='https://picsum.photos/seed/uzvar/480/340'),
    dict(name='Кава по-віденськи', category='drink', price=65,
         description='Еспресо зі збитими вершками.',
         ingredients='Еспресо, вершки',
         photo_url='https://picsum.photos/seed/vienna-coffee/480/340'),
    dict(name='Лимонад «М\u2019ята-огірок»', category='drink', price=70,
         description='Освіжаючий лимонад із м\u2019ятою та огірком.',
         ingredients='Лимон, м\u2019ята, огірок, содова',
         photo_url='https://picsum.photos/seed/lemonade/480/340'),
]

TABLES = [
    dict(number=1, seats=2, pos_x=8, pos_y=16),
    dict(number=2, seats=2, pos_x=8, pos_y=38),
    dict(number=3, seats=2, pos_x=8, pos_y=60),
    dict(number=4, seats=2, pos_x=8, pos_y=82),
    dict(number=5, seats=4, pos_x=37, pos_y=28),
    dict(number=6, seats=4, pos_x=58, pos_y=28),
    dict(number=7, seats=4, pos_x=37, pos_y=62),
    dict(number=8, seats=4, pos_x=58, pos_y=62),
    dict(number=9, seats=6, pos_x=88, pos_y=24, is_vip=True),
    dict(number=10, seats=6, pos_x=88, pos_y=60, is_vip=True),
    dict(number=11, seats=4, pos_x=28, pos_y=92, is_terrace=True),
    dict(number=12, seats=4, pos_x=68, pos_y=92, is_terrace=True),
]


class Command(BaseCommand):
    help = 'Наповнює базу демонстраційними стравами, столиками та тестовим користувачем.'

    def handle(self, *args, **options):
        created_dishes = 0
        for data in DISHES:
            data.setdefault('available', True)
            _, created = Dish.objects.get_or_create(name=data['name'], defaults=data)
            created_dishes += int(created)

        created_tables = 0
        for data in TABLES:
            _, created = RestaurantTable.objects.get_or_create(number=data['number'], defaults=data)
            created_tables += int(created)

        demo_user, user_created = User.objects.get_or_create(
            username='guest', defaults={'first_name': 'Гість'}
        )
        if user_created:
            demo_user.set_password('guest12345')
            demo_user.save()

        if not Review.objects.exists():
            greek = Dish.objects.filter(name='Салат «Грецький»').first()
            borsch = Dish.objects.filter(name='Борщ український').first()
            if greek:
                Review.objects.create(dish=greek, user=demo_user, rating=5, text='Дуже свіжо, фети не пожаліли.')
            if borsch:
                Review.objects.create(dish=borsch, user=demo_user, rating=5, text='Смак дитинства, готують чудово.')

        self.stdout.write(self.style.SUCCESS(
            f'Готово: додано {created_dishes} страв, {created_tables} столиків. '
            f'Тестовий користувач: guest / guest12345.'
        ))
