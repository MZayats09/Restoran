from decimal import Decimal

from .models import Dish

CART_SESSION_KEY = 'cart'


class Cart:
    """A simple shopping cart stored in the Django session.

    Session layout: {"<dish_id>": <quantity>, ...}
    """

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if cart is None:
            cart = self.session[CART_SESSION_KEY] = {}
        self.cart = cart

    def add(self, dish, quantity=1):
        dish_id = str(dish.pk)
        if dish_id in self.cart:
            self.cart[dish_id] += quantity
        else:
            self.cart[dish_id] = quantity
        self.save()

    def set_quantity(self, dish_id, quantity):
        dish_id = str(dish_id)
        if quantity <= 0:
            self.remove(dish_id)
            return
        if dish_id in self.cart:
            self.cart[dish_id] = quantity
            self.save()

    def remove(self, dish_id):
        dish_id = str(dish_id)
        if dish_id in self.cart:
            del self.cart[dish_id]
            self.save()

    def clear(self):
        self.session[CART_SESSION_KEY] = {}
        self.save()

    def save(self):
        self.session.modified = True

    def replace_with(self, items):
        """items: iterable of (dish_id, quantity) — used by 'order again'."""
        self.session[CART_SESSION_KEY] = {str(k): v for k, v in items}
        self.save()

    def __iter__(self):
        dish_ids = self.cart.keys()
        dishes = Dish.objects.filter(pk__in=dish_ids)
        dishes_by_id = {str(d.pk): d for d in dishes}
        for dish_id, quantity in self.cart.items():
            dish = dishes_by_id.get(dish_id)
            if not dish:
                continue
            yield {
                'dish': dish,
                'quantity': quantity,
                'subtotal': dish.price * quantity,
            }

    def __len__(self):
        return len(self.cart)

    def total_quantity(self):
        return sum(self.cart.values())

    def total_price(self):
        return sum(Decimal(item['subtotal']) for item in self)
