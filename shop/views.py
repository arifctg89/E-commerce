from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Register
from .cart import Cart

from django.contrib import messages


from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter


from .forms import CheckoutForm


from .models import Order, OrderItem

from reportlab.lib import colors
from reportlab.lib.units import inch


import os
from django.conf import settings
from django.contrib.staticfiles import finders # Helps find static files in development


# Create your views here.


def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            # ডাটাবেজে এই ইমেইল এবং পাসওয়ার্ডের কোনো ইউজার আছে কিনা চেক করা
            user = Register.objects.get(email=email, password=password)
            
            # সেশনে ইউজারের আইডি সেভ করে রাখা (যাতে সিস্টেম মনে রাখতে পারে কে লগইন করেছে)
            request.session['user_id'] = user.id
            messages.success(request, f"Welcome back, {user.full_name}!")
            return redirect('product_list') # লগইন সফল হলে শপিং পেজে নিয়ে যাবে
            
        except Register.DoesNotExist:
            messages.error(request, "Invalid Email or Password!")
            return redirect('login')

    return render(request, 'shop/login.html')


def logout_view(request):
    if 'user_id' in request.session:
        del request.session['user_id'] # সেশন থেকে আইডি ডিলিট করা
    messages.success(request, "Logged out successfully!")
    return redirect('login')

def register(request):
    if request.method == "POST":

        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        add_home = request.POST.get('add_home')
        add_office = request.POST.get('add_office')
        reg_phone = request.POST.get('reg_phone')
        password = request.POST.get('password')


# 🚨 ইমেইলটি ইতিমধ্যে ডাটাবেজে আছে কিনা তা চেক করা হচ্ছে
        if Register.objects.filter(email=email).exists():
            # যদি ইমেইল মিলে যায়, তবে এরর মেসেজ পাঠানো হবে
            messages.error(request, "This email is already in use! Try another email.")
            return redirect('register') # নতুন করে সেভ না করে পেজটি আবার দেখাবে

        # Create & save new user in database
        new_user = Register(
            full_name=full_name,
            email=email,
            add_home=add_home,
            add_office=add_office,
            reg_phone=reg_phone,
            password=password
        )
        new_user.save()

        request.session['checkout_data'] = {
            'full_name': full_name,
            'email': email,
            'phone': reg_phone,
            'address': add_home, # অথবা add_office দিতে পারেন
        }


        # Registration massage
        messages.success(request, "Registration Successful!")
        return redirect('register')  # refresh & redirect

    return render(request, 'shop/register.html')




def edit_profile_page(request):
    # সেশনে ইউজার আইডি আছে কিনা চেক করা (লগইন ছাড়া কেউ এই পেজে আসতে পারবে না)
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please login first!")
        return redirect('login')
    
    # লগইন করা ইউজারের ডাটা ডাটাবেজ থেকে আনা
    user_data = Register.objects.get(id=user_id)

    if request.method == "POST":
        # ইউজার যদি তার প্রোফাইল আপডেট/এডিট করতে চায়
        user_data.full_name = request.POST.get('full_name')
        user_data.add_home = request.POST.get('add_home')
        user_data.add_office = request.POST.get('add_office')
        user_data.reg_phone = request.POST.get('reg_phone')
        # ইচ্ছা হলে পাসওয়ার্ডও আপডেট করতে পারেন
        
        user_data.save() # আপডেট করা ডাটা সেভ হবে
        messages.success(request, "Profile updated successfully!")
        return redirect('edit_profile_page')

    # এখানে আপনার ই-কমার্সের প্রোডাক্টগুলোও পাঠাতে পারেন (যেমন: Products.objects.all())
    return render(request, 'shop/edit_profile.html', {'user': user_data})




def product_list(request):
    products = Product.objects.all()
    return render(request, 'shop/list.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'shop/detail.html', {'product': product})




def cart_add(request, product_id):
    cart = Cart(request)
    product = Product.objects.get(id=product_id)
    size = request.POST.get('size')
    quantity = int(request.POST.get('quantity', 1))
    cart.add(product=product,quantity=quantity, size=size)
    return redirect('cart_detail')



def cart_detail(request):
    cart = Cart(request)
    return render(request, 'shop/cart_detail.html', {'cart': cart})


def cart_remove(request, product_id):
    cart = Cart(request)
    size = request.GET.get('size')
    cart.remove(product_id=product_id, size=size)
    next_url = request.META.get('HTTP_REFERER')
    if next_url:
        return redirect(next_url)
    return redirect('cart_detail')


def cart_update(request, product_id):
    cart = Cart(request)
    quantity = request.POST.get('quantity')
    size = request.POST.get('size')
    
    cart.update_quantity(product_id=product_id, quantity=quantity, size=size)
    return redirect('cart_detail')




def checkout(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # 1. Create the order
            total = cart.get_total_price()
            order = Order.objects.create(
                full_name=form.cleaned_data['full_name'],
                email=form.cleaned_data['email'],
                address=form.cleaned_data['address'],
                phone=form.cleaned_data['phone'],
                total_paid=total
            )
            # 2. Save items (This doesn't involve the session)
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity'],
                    size=item['size']
                )

            # 3. ONLY store the ID in the session (Integers are JSON serializable!)
            request.session['checkout_info'] = form.cleaned_data
            request.session['order_id'] = str(order.id) 
            return redirect('checkout_success')
    else:
        saved_data = request.session.get('checkout_data', {})
        form = CheckoutForm(initial={
            'full_name': saved_data.get('full_name', ''),
            'email': saved_data.get('email', ''),
            'phone': saved_data.get('phone', ''),
            'address': saved_data.get('address', ''), # অথবা add_home/add_office আপনার ফর্মের ফিল্ড অনুযায়ী
        })
    
    return render(request, 'shop/checkout.html', {'cart': cart, 'form': form})




def download_cart_pdf(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    user_info = request.session.get('checkout_info', {})
    cart = Cart(request)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{order.id}.pdf"'
    response['Content-Disposition'] = f'inline; filename="Invoice_{order.id}.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    p.setFillColor(colors.dodgerblue)
    p.rect(0, height - 80, width, 80, fill=1, stroke=0)

    # --- STEP 1: DRAW THE BANNER FIRST ---
    p.setFillColor(colors.dodgerblue)
    p.rect(0, height - 80, width, 80, fill=1, stroke=0)
    
    # --- STEP 2: DRAW THE LOGO ON TOP ---
    logo_path = finders.find('shop/images/logo.png')
    if logo_path:
        # We use a y-coordinate slightly above the bottom of the banner
        p.drawImage(logo_path, 0.5 * inch, height - 70, width=1.5 * inch, height=0.6 * inch, preserveAspectRatio=True, mask='auto')
    else:
        # This helps you debug: if the logo is missing, you'll see this in your console
        print("LOGO NOT FOUND AT: shop/images/logo.png")

    # --- STEP 3: DRAW THE TEXT ---
    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 24)
    p.drawString(2.5 * inch, height - 55, "OFFICIAL INVOICE")

    
    # --- Company & Customer Info ---
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(1 * inch, height - 120, "Billed To:")
    p.setFont("Helvetica", 11)
    p.drawString(1 * inch, height - 135, f"Full Name: {order.full_name}")
    p.drawString(1 * inch, height - 150, f"Email: {order.email}")
    p.drawString(1 * inch, height - 165, f"Phone: {order.phone}")
    p.drawString(1 * inch, height - 180, f"Address: {order.address}")

    p.setFont("Helvetica-Bold", 12)
    p.drawString(4 * inch, height - 120, "Order Details:")
    p.setFont("Helvetica", 11)
    p.drawString(4 * inch, height - 135, f"Order ID: {order.formatted_id}")
    p.drawString(4 * inch, height - 150, f"Date: {order.created_at.strftime('%Y-%m-%d')}")

    # --- Table Header ---
    y = height - 220
    p.setFillColor(colors.whitesmoke)
    p.rect(0.8 * inch, y - 5, 6.9 * inch, 20, fill=1, stroke=0)
    p.setFillColor(colors.black)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(1 * inch, y, "Product Name")
    p.drawString(4 * inch, y, "Qty")
    p.drawString(5 * inch, y, "Unit Price")
    p.drawString(6.5 * inch, y, "Total")

    # --- Items ---
    p.setFont("Helvetica", 11)
    for item in cart:
        y -= 25
        p.drawString(1 * inch, y, f"{item['product'].name[:35]}")
        p.drawString(4 * inch, y, f"{item['quantity']}")
        p.drawString(5 * inch, y, f"${item['price']}")
        p.drawString(6.5 * inch, y, f"${item['total_price']}")
        
        # Draw subtle line between items
        p.setStrokeColor(colors.lightgrey)
        p.line(0.8 * inch, y - 5, 7.7 * inch, y - 5)

    # --- Grand Total ---
    y -= 40
    p.setFont("Helvetica-Bold", 14)
    p.drawRightString(7.3 * inch, y, f"Grand Total: ${cart.get_total_price()}")

    # Footer
    p.setFont("Helvetica-Oblique", 9)
    p.setFillColor(colors.grey)
    p.drawCentredString(width / 2, 0.5 * inch, "Thank you for shopping with us!")

    p.showPage()
    p.save()
    return response



def checkout_success(request):
    order_id = request.session.get('order_id')
    if not order_id:
        return redirect('product_list')
    
    return render(request, 'shop/success.html', {'order_id': order_id})


def clear_checkout_session(request):
    # List of keys we want to wipe
    keys_to_clear = ['cart', 'order_id', 'checkout_info']
    
    for key in keys_to_clear:
        if key in request.session:
            del request.session[key]
            
    # Mark session as modified to ensure it saves
    request.session.modified = True
    
    # Redirect back to the home page or product list
    return redirect('product_list')



def contact(request):
    return render(request, 'shop/contact.html')