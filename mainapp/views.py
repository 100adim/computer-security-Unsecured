import os
import hashlib
import random
import string
from django.shortcuts import render, redirect
from django.db import connection
from django.conf import settings
from .models import User, Customer
from django.db import IntegrityError
from django.core.mail import send_mail


def home(request):
    return render(request, "mainapp/home.html")

def register(request):
    error = ""
    if request.method == "POST":
        username = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        email = request.POST.get("email")

        if password1 != password2:
            return render(request, "mainapp/register.html", {"error": "Passwords do not match"})

        raw_query = """
        INSERT INTO mainapp_user (username, email, password_hash, salt)
        VALUES (%s, %s, %s, %s)
        """

        try:
            with connection.cursor() as cursor:
                cursor.execute(raw_query, [username, email, password1, b''])
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
            request.session['username'] = username  
            return render(request, "mainapp/system.html", {"username": username})
        else:
            error = "Invalid username or password"

    return render(request, "mainapp/login.html", {"error": error})

def add_customer(request):
    if request.method == "POST":
        if 'username' not in request.session:
            return redirect('login')

        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        id_number = request.POST.get("id_number")
        created_by = request.session.get("username")

        try:
            customer = Customer.objects.create(
                first_name=first_name,
                last_name=last_name,
                id_number=id_number,
                created_by=created_by
            )
        except IntegrityError:
            return render(request, "mainapp/add_customer.html", {
                "error": "This ID Number already exists in the system."
            })
        except Exception as e:
            return render(request, "mainapp/add_customer.html", {
                "error": f"Failed to add customer: {str(e)}"
            })

        return render(request, "mainapp/system.html", {"new_customer": customer})

    return render(request, "mainapp/add_customer.html")

def customer_list(request):
    username = request.session.get("username")
    customers = Customer.objects.filter(created_by=username)
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

        send_mail(
            subject="Communication LTD - Reset Code",
            message=f"Hello {username},\n\nHere is your reset code:\n{sha1_code}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

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
