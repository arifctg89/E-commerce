from decimal import Decimal
from .models import Product

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    # UPDATED: Added 'size' parameter
    def add(self, product, quantity=1, size=None, override_quantity=False):
        product_id = f"{product.id}-{size}" if size else str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {
                'product_id': str(product.id),
                'quantity': 0,
                'price': str(product.price),
                'size': size,  # ✅ Store the selected size
            }
        
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
            
        self.save()

    def save(self):
        self.session.modified = True

    def __iter__(self):
        product_ids = self.cart.keys()
        product_ids = [item['product_id'] for item in self.cart.values()]
        products = Product.objects.filter(id__in=product_ids)
        
        product_map = {str(p.id): p for p in products}

        for product_id, item in self.cart.items():
            yield_item = item.copy() 
            yield_item['product'] = product_map.get(str(item['product_id']))
            yield_item['price'] = Decimal(item['price'])
            
            # ✅ Pass the size to the yield_item so it's accessible in HTML
            yield_item['size'] = item.get('size')
            yield_item['product_id'] = product_id 
            
            yield_item['total_price'] = yield_item['price'] * yield_item['quantity']
            yield yield_item

    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def remove(self, product_id, size=None ):
        product_id = f"{product_id}-{size}" if size else str(product_id)
        if product_id in self.cart:
                    del self.cart[product_id]
                    self.save()

    def update_quantity(self, product_id, quantity, size=None):
        product_id = f"{product_id}-{size}" if size else str(product_id)
        if product_id in self.cart:
            self.cart[product_id]['quantity'] = int(quantity)
            self.save()

    def clear(self):
        if 'cart' in self.session:
            del self.session['cart']
            self.save()