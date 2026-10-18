from django.contrib import admin
from .models import Product, Size, Order, OrderItem, Register


# Register your models here.

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    search_fields = ('size',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    # This adds a sidebar in Admin to filter by Category and Shipping
    list_display = ('name', 'category', 'price', 'shipping')
    list_filter = ('category', 'shipping') 
    search_fields = ('name',)
    filter_horizontal = ('size',)



class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['formatted_id', 'full_name', 'email', 'phone', 'total_paid', 'created_at']
    inlines = [OrderItemInline]


@admin.register(Register)
class RegisterAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'add_home', 'add_office', 'reg_phone','password')
    search_fields = ('full_name', 'email')

#admin.site.register(Register)