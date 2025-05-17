import os
import hashlib
import random
import string
from django.shortcuts import render, redirect
from django.db import connection
from django.conf import settings
from .models import User, Customer

def home(request):
    return render(request, "mainapp/home.html")

def register(request):
    error = ""
    if request.method == "POST":
        username = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        email = settings.DEFAULT_USER_EMAIL

        if password1 != password2:
            return render(request, "mainapp/register.html", {"error": "Passwords do not match"})

        raw_query = f"""
        INSERT INTO mainapp_user (username, email, password_hash, salt)
        VALUES ('{username}', '{email}', '{password1}', '')
        """

        try:
            with connection.cursor() as cursor:
                cursor.execute(raw_query)
        except Exception as e:
            error = f"Registration failed: {str(e)}"
            return render(request, "mainapp/register.html", {"error": error})

        return redirect("login")

    return render(request, "mainapp/register.html")

def login_view(request):
    error = ""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        raw_query = f"SELECT * FROM mainapp_user WHERE username = '{username}' AND password_hash = '{password}'"
        with connection.cursor() as cursor:
            cursor.execute(raw_query)
            user = cursor.fetchone()

        if user:
            return render(request, "mainapp/system.html", {"username": username})
        else:
            error = "Invalid username or password"

    return render(request, "mainapp/login.html", {"error": error})

def add_customer(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        id_number = request.POST.get("id_number")

        try:
            customer = Customer.objects.create(
                first_name=first_name,
                last_name=last_name,
                id_number=id_number
            )
        except Exception as e:
            return render(request, "mainapp/add_customer.html", {"error": f"Failed to add customer: {str(e)}"})

        return render(request, "mainapp/system.html", {"new_customer": customer})

    return render(request, "mainapp/add_customer.html")

def customer_list(request):
    customers = Customer.objects.all()
    return render(request, "mainapp/customer_list.html", {"customers": customers})

def forgot_password(request):
    if request.method == "POST":
        username = request.POST.get("username")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return render(request, "mainapp/forgot_password.html", {"error": "Username not found."})

        reset_code = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        sha1_code = hashlib.sha1(reset_code.encode()).hexdigest()

        request.session['reset_code'] = sha1_code
        request.session['reset_username'] = username

        return render(request, "mainapp/verify_reset_code.html", {"reset_code": sha1_code})

    return render(request, "mainapp/forgot_password.html")

def verify_reset_code(request):
    if request.method == "POST":
        entered_code = request.POST.get("reset_code")
        saved_code = request.session.get("reset_code")

        if entered_code == saved_code:
            return redirect("reset_password")
        else:
            return render(request, "mainapp/verify_reset_code.html", {"error": "Invalid reset code."})

    return render(request, "mainapp/verify_reset_code.html", {"reset_code": request.session.get("reset_code")})

def reset_password(request):
    if request.method == "POST":
        new_password1 = request.POST.get("new_password1")
        new_password2 = request.POST.get("new_password2")
        username = request.session.get("reset_username")

        if new_password1 != new_password2:
            return render(request, "mainapp/reset_password.html", {"error": "Passwords do not match."})

        try:
            raw_query = f"UPDATE mainapp_user SET password_hash = '{new_password1}' WHERE username = '{username}'"
            with connection.cursor() as cursor:
                cursor.execute(raw_query)
        except Exception as e:
            return render(request, "mainapp/reset_password.html", {"error": str(e)})

        return redirect("login")

    return render(request, "mainapp/reset_password.html")
