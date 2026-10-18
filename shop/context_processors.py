from .cart import Cart
from .models import Register

def cart_count(request):
    """Returns the total number of items in the cart for all templates."""
    cart = Cart(request)
    # This sums up the 'quantity' of all items in the session
    total_items = sum(item['quantity'] for item in cart.cart.values())
    return {'cart_total_count': total_items}

def get_logged_in_user(request):
    user_id = request.session.get('user_id')
    if user_id:
        try:
            # সেশনের আইডি দিয়ে ডাটাবেজ থেকে ইউজারকে খুঁজে বের করা
            user = Register.objects.get(id=user_id)
            return {'logged_in_user': user}
        except Register.DoesNotExist:
            pass
    return {'logged_in_user': None}
