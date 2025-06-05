import hmac
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
    #return render(request, "mainapp/home.html")
    username = request.session.get('username')
    new_customer = request.session.pop('new_customer', None)
    if username:
        return render(request, 'mainapp/system.html', {
            'username': username,
            'new_customer': new_customer
        })
    else:
        return render(request, 'mainapp/home.html')

def register(request):
    error = ""
    if request.method == "POST":
        username = request.POST.get("username")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")
        email = request.POST.get("email")

        if password1 != password2:
            return render(request, "mainapp/register.html", {"error": "Passwords do not match"})

        # raw_query = f"""
        # INSERT INTO mainapp_user (username, email, password_hash, salt)
        # VALUES ('{username}', '{email}', '{password1}', '')
        # """
        salt = os.urandom(16)
        password_hash = hmac.new(salt, password1.encode(), hashlib.sha256).hexdigest()
        salt_hex = salt.hex()

        try:
            with connection.cursor() as cursor:
                # cursor.execute(raw_query)
                cursor.executescript(f"""
                    INSERT INTO mainapp_user (username, email, password_hash, salt)
                    VALUES ('{username}', '{email}', '{password_hash}', '{salt_hex}');
                """)

        except Exception as e:
            error = f"Registration failed: {str(e)}"
            print(f"Registration failed: {e}")

            return render(request, "mainapp/register.html", {"error": error})

        return redirect("login")

    return render(request, "mainapp/register.html")

def login_view(request):
    error = ""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # try:
        #     user = User.objects.get(username=username)
        # except User.DoesNotExist:
        #     return render(request, 'mainapp/login.html', {'error': 'Invalid username or password.'})
        raw_query = f"""
            SELECT username, password_hash, salt 
            FROM mainapp_user 
            WHERE username = '{username}'
        """
        with connection.cursor() as cursor:
            cursor.execute(raw_query)
            result = cursor.fetchone()
        if result:
            db_username, db_password_hash, db_salt = result
        else:
            return render(request, 'mainapp/login.html', {'error': 'Invalid username or password.'})
        salt = db_salt
        if isinstance(salt, str):
            salt = bytes.fromhex(salt)
        new_hash = hmac.new(salt, password.encode(), hashlib.sha256).hexdigest()
        print(f"Salt: {salt}")
        print(f"Password: {password}")
        print(f"Hash: {new_hash}")
        print(f"pass_hash: {db_password_hash}")


        raw_query = f"SELECT * FROM mainapp_user WHERE username = '{username}' AND password_hash = '{new_hash}'"
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
    username = request.session.get('username')
    if not username:
        return redirect('login')
    if request.method == "POST":
        if 'username' not in request.session:
            return redirect('login')

        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        id_number = request.POST.get("id_number")

        try:
            # customer = Customer.objects.create(
            #     first_name=first_name,
            #     last_name=last_name,
            #     id_number=id_number
            # )
            query = f"""
                            INSERT INTO mainapp_customer (first_name, last_name, id_number, created_by)
                            VALUES ('{first_name}', '{last_name}', '{id_number}','{username}');
                        """
            with connection.cursor() as cursor:
                cursor.executescript(query)
               # cursor.execute("SELECT * FROM mainapp_customer")
                request.session['new_customer'] = {
                    "first_name": first_name,
                    "last_name": last_name
                }
                #customer = cursor.fetchone()
                return redirect('home')
                #return render(request, "mainapp/system.html", {"new_customer": customer})
        except IntegrityError as IE:
            print(f"Exception occurred: {IE}")
            return render(request, "mainapp/add_customer.html", {
                "error": "This ID Number already exists in the system."
            })
        except Exception as e:
            print(f"Exception occurred: {e}")
            return render(request, "mainapp/add_customer.html", {
                "error": f"Failed to add customer: {str(e)}"
            })
    return render(request, "mainapp/add_customer.html")

def customer_list(request):
    username = request.session.get("username")
    customers = Customer.objects.filter()
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

        return redirect("verify_reset_code")

        #render(request, "mainapp/verify_reset_code.html", {"reset_code": sha1_code})

    return render(request, "mainapp/forgot_password.html")

def verify_reset_code(request):
    if request.method == "POST":
        entered_code = request.POST.get("reset_code")
        saved_code = request.session.get("reset_code")
        print(saved_code)

        if entered_code == saved_code:
            return redirect("reset_password")
        else:
            return render(request, "mainapp/verify_reset_code.html", {"error": "Invalid reset code."})

    return render(request, "mainapp/verify_reset_code.html", {"reset_code": request.session.get("reset_code")})

def reset_password(request):
    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password1 = request.POST.get("new_password1")
        new_password2 = request.POST.get("new_password2")
        username = request.session.get("reset_username")

        if new_password1 != new_password2:
            return render(request, "mainapp/reset_password.html", {"error": "Passwords do not match."})

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return render(request, "mainapp/reset_password.html", {"error": "User not found."})

        # בדיקת הסיסמה הנוכחית (לא מאובטחת - טקסט רגיל)
        if current_password.strip() != user.password_hash.strip():
            return render(request, "mainapp/reset_password.html", {"error": "Incorrect current password."})

        # עדכון הסיסמה (ללא אבטחה)
        user.password_hash = new_password1
        user.save()

        return redirect("login")

    return render(request, "mainapp/reset_password.html")


def user_list(request):
    users = User.objects.all()
    return render(request, 'mainapp/user_list.html', {'users': users})
def logout_user(request):
    request.session.flush()
    return redirect('home')


def change_password(request):
    username = request.session.get('username', '')
    if not username:
        return redirect('login')

    if request.method == 'POST':
        new_password1 = request.POST.get('new_password1', '')
        new_password2 = request.POST.get('new_password2', '')

        if new_password1 != new_password2:
            return render(request, 'mainapp/reset_password.html', {'error': 'Passwords do not match.'})

        # is_valid, error_message = is_password_valid(new_password1)
        # if not is_valid:
        #     return render(request, 'mainapp/reset_password.html', {'error': error_message})

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return render(request, 'mainapp/reset_password.html', {'error': 'User not found.'})

        new_password_hash_check = hmac.new(bytes.fromhex(user.salt), new_password1.encode(), hashlib.sha256).hexdigest()
        previous_hashes = [user.password_hash, user.previous_password_hash1, user.previous_password_hash2, user.previous_password_hash3]
        if new_password_hash_check in previous_hashes:
            return render(request, 'mainapp/reset_password.html', {'error': 'New password must be different from the last 3 passwords.'})

        user.previous_password_hash3 = user.previous_password_hash2
        user.previous_password_hash2 = user.previous_password_hash1
        user.previous_password_hash1 = user.password_hash

        new_salt = os.urandom(16)

        new_password_hash = hmac.new(new_salt, new_password1.encode(), hashlib.sha256).hexdigest()

        user.salt = new_salt
        user.password_hash = new_password_hash
        print(f"salt type: {type(user.salt)}")  # לוודא שזה str
        print(f"salt value: {user.salt}")  # לוודא שזה hex string
        user.full_clean()
        user.save()

        return redirect('home')

    return render(request, 'mainapp/reset_password.html')