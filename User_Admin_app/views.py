from django.shortcuts import render, redirect ,get_object_or_404
from django.contrib import messages
from .models import CustomUser


# 🏠 Home Page
def home_page(request):
    return render(request, 'home.html')


# 🧍‍♂️ Register Page
def register_page(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        mobile = request.POST.get('mobile')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        agree = request.POST.get('agree')

        # Validation
        if not agree:
            messages.error(request, 'Please agree to the terms and conditions.')
            return redirect('register_page')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('register_page')

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register_page')

        # Save user
        CustomUser.objects.create(
            full_name=full_name,
            email=email,
            username=username,
            mobile=mobile,
            password=password,
            confirm_password=confirm_password,
            agree=True
        )

        messages.success(request, 'Registration successful! You can now login.')
        return redirect('login_page')

    return render(request, 'register.html')


# 🔐 Login Page
def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = CustomUser.objects.get(username=username, password=password)
        except CustomUser.DoesNotExist:
            messages.error(request, 'Invalid username or password.')
            return redirect('login_page')

        # ✅ Store session details
        request.session['user_id'] = user.id
        request.session['username'] = user.username
        request.session['full_name'] = user.full_name

        messages.success(request, f'Welcome, {user.full_name}!')
        return redirect('user_dashboard')

    return render(request, 'login.html')


# 🧱 User Dashboard
def user_dashboard(request):
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Please login first.")
        return redirect('login_page')

    user = CustomUser.objects.get(id=user_id)
    return render(request, 'user_dashboard.html', {'user': user})


# 🚪 Logout
def logout_user(request):
    request.session.flush()
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home_page')

# 📋 Admin Dashboard
# 🧑‍💼 Admin Login
def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Hardcoded admin credentials (you can customize)
        if username == 'admin' and password == 'admin':
            request.session['is_admin'] = True
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid admin credentials!')
            return redirect('admin_login')

    return render(request, 'admin_login.html')


# 📋 Admin Dashboard
def admin_dashboard(request):
    if not request.session.get('is_admin'):
        messages.error(request, 'Access denied! Please login as admin.')
        return redirect('admin_login')

    users = CustomUser.objects.all()
    return render(request, 'admin_dashboard.html', {'users': users})


# ✅ Approve User Function
def approve_user(request, user_id):
    if not request.session.get('is_admin'):
        return redirect('admin_login')

    user = get_object_or_404(CustomUser, id=user_id)
    user.is_approved = True
    user.save()
    messages.success(request, f"{user.username} has been approved successfully!")
    return redirect('admin_dashboard')


# ❌ Reject User Function
def reject_user(request, user_id):
    if not request.session.get('is_admin'):
        return redirect('admin_login')

    user = get_object_or_404(CustomUser, id=user_id)
    user.is_approved = False
    user.save()
    messages.warning(request, f"{user.username} has been rejected!")
    return redirect('admin_dashboard')

