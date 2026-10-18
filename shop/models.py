from django.db import models

# 1. New Size Model to store individual size options
class Size(models.Model):
    size = models.CharField(max_length=20) # e.g., "S", "XL", "42"

    def __str__(self):
        return self.size

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('All', 'All'),
        ('Cloths Male', 'Cloths Male'),
        ('Cloths Female', 'Cloths Female'),
        ('Footwear Male', 'Footwear Male'),
        ('Footwear Female', 'Footwear Female'),
        ('Telephones', 'Telephones'),
        ('Tablets', 'Tablets'),
        ('Televisions', 'Televisions'),
        ('Computers', 'Computers'),
        ('Headphones', 'Headphones'),
        ('Smart home', 'Smart home'),
        ('Other', 'Other'),
    ]

    SHIPPING_CHOICES = [
        ('Free', 'Free Shipping'),
        ('Paid', 'Paid Shipping'),
    ]

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='All')
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # This allows you to select multiple sizes in the Admin panel
    size = models.ManyToManyField(Size) 
    
    shipping = models.CharField(max_length=20, choices=SHIPPING_CHOICES, default='Free')
    image_url = models.URLField(blank=True, null=True)
    image_file = models.ImageField(upload_to='products/', blank=True, null=True)

    Stock = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    Sold = models.DecimalField(max_digits=10, decimal_places=0, default=0)

    @property
    def price_range(self):
        if self.price <= 100:
            return "$0-$100"
        elif 101 <= self.price <= 5000:
            return "$101-$5000"
        elif 5001 <= self.price <= 10000:
            return "$5001-$10000"
        else:
            return "$10000+"

    def __str__(self):
        return f"{self.name} ({self.category})"

class Order(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.TextField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    shipping_method = models.CharField(max_length=20, default='Free Shipping')

    @property
    def formatted_id(self):
        return f"ARE-{self.id:05d}"

    def __str__(self):
        return f"Order {self.formatted_id} by {self.full_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    
    # We keep this as a CharField to save the SPECIFIC size chosen at checkout
    size = models.CharField(max_length=20, blank=True, null=True)
    def __str__(self):
        return f"Item {self.id} (Order {self.order.formatted_id})"

    @property
    def total_item_price(self):
        return self.price * self.quantity
    



class Register(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    add_home = models.TextField()
    add_office = models.TextField()
    reg_phone = models.CharField(max_length=20, blank=True, null=True)
    password = models.CharField(max_length=100)


    def __str__(self):
        return self.full_name