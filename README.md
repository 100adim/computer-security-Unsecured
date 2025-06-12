# 🚨 Communication LTD Unsecured - Vulnerability Demonstration Project

![Vulnerability Demo](https://img.shields.io/badge/Purpose-Educational_Vulnerability_Demo-red?style=for-the-badge&logo=security) ![Django](https://img.shields.io/badge/Django-5.2-darkred?style=for-the-badge&logo=django) ![Python](https://img.shields.io/badge/Python-3.8+-red?style=for-the-badge&logo=python) ![Dangerous](https://img.shields.io/badge/⚠️-DANGEROUS_CODE-red?style=for-the-badge)

## ⚠️ **CRITICAL WARNING**

This is the **deliberately insecure version** of the Communication LTD project, designed to demonstrate common web application vulnerabilities and their exploitation techniques.

---

## 📋 **Table of Contents**

- [🎯 Vulnerabilities](#-vulnerabilities)
- [🏗️ Architecture](#️-architecture)
- [🚀 Quick Start](#-quick-start)
- [💉 SQL Injection Demonstrations](#-sql-injection-demonstrations)
- [🚨 XSS Attack Demonstrations](#-xss-attack-demonstrations)
- [📖 Detailed Setup](#-detailed-setup)
- [📚 Vulnerability Documentation](#-vulnerability-documentation)
- [🛠️ Technology Stack](#️-technology-stack)

---

## 🎯 **Vulnerabilities**

### 💉 **SQL Injection Vulnerabilities**
- **Authentication Bypass** in login system
- **Data Destruction** via registration form
- **Data Manipulation** through customer management

### 🚨 **XSS Vulnerabilities**
- **Stored XSS** in customer names and data
- **Session Hijacking** through malicious scripts
- **Script Injection** in all user input fields
- **DOM Manipulation** attacks

### 🔓 **Missing Security Controls**
- **No Input Validation** - Accepts any user input
- **No Output Escaping** - Uses dangerous `|safe` filters
- **No Password Policy** - Weak passwords allowed
- **No Brute Force Protection** - Unlimited login attempts
- **Information Disclosure** - Exposes sensitive data

---

## 🏗️ **Architecture**

```
computer-security-Unsecured/ # Project root directory (VULNERABLE VERSION)
|-- communication_ltd/       # Main Django project settings directory
|   |-- __init__.py
|   |-- asgi.py
|   |-- config.json          # Security configuration (partially ignored)
|   |-- settings.py          # Django settings (some security disabled)
|   |-- urls.py              # URL configurations
|   +-- wsgi.py
|-- db.sqlite3               # SQLite database (vulnerable to injection)
|-- mainapp/                 # Primary Django application (VULNERABLE)
|   |-- __init__.py
|   |-- apps.py              # App configuration
|   |-- migrations/          # Database schema changes
|   |   |-- 0001_initial.py
|   |   |-- 0002_customer_alter_user_password_hash_and_more.py
|   |   |-- 0003_user_previous_password_hash1_and_more.py
|   |   |-- 0004_customer_created_by.py
|   |   +-- __init__.py
|   |-- models.py            # Database models (vulnerable structure)
|   |-- static/              # Static files
|   |   +-- mainapp_static/
|   |       +-- style.css
|   |-- templates/           # Template files (VULNERABLE TO XSS)
|   |   +-- mainapp/
|   |       |-- add_customer.html      # XSS vulnerable input forms
|   |       |-- base.html
|   |       |-- customer_list.html     # XSS vulnerable display (|safe filters)
|   |       |-- forgot_password.html   # Information disclosure
|   |       |-- home.html
|   |       |-- login.html             # SQL injection entry point
|   |       |-- register.html          # SQL injection entry point
|   |       |-- reset_password.html
|   |       |-- system.html            # XSS vulnerable dashboard
|   |       |-- user_list.html
|   |       +-- verify_reset_code.html
|   |-- tests.py
|   |-- urls.py              # URL routing (vulnerable endpoints)
|   +-- views.py             # VULNERABLE BUSINESS LOGIC
|-- manage.py
+-- system/                  # Additional Django application
    |-- __init__.py
    |-- admin.py
    |-- apps.py
    |-- migrations/
    |   +-- __init__.py
    |-- models.py
    +-- tests.py
```

### **🔗 Vulnerability Flow**
```mermaid
graph TD
    A[Malicious User Input] --> B[No Input Validation]
    B --> C[Raw SQL Injection]
    C --> D[Database Compromise]
    D --> E[XSS Script Injection]
    E --> F[Session Hijacking]
    F --> G[Complete System Takeover]
```

---

## 🚀 **Quick Start**

### **⚡ 1-Minute Dangerous Setup**
```bash
# Clone the vulnerable repository
git clone https://github.com/100adim/computer-security-Unsecured
cd computer-security-Unsecured

# Setting Up Virtual Environment (recommended for isolation)
python -m venv vulnerable_env
source vulnerable_env/bin/activate  # macOS/Linux
vulnerable_env\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Initialize vulnerable database
python manage.py makemigrations mainapp
python manage.py migrate

# Run the VULNERABLE application
python manage.py runserver 8001
```

**🌐 Access:** http://localhost:8001

**⚠️ WARNING:** This application is intentionally vulnerable!

---


### **🎯 Attack 1: Authentication Bypass**

# mainapp/views.py - login_view() function

#### **Attack Payload:**

```sql
Username: admin' OR '1'='1' --
Password: Anything123!
```

---

### **🎯 Attack 2: Database Destruction**

# mainapp/views.py - register() function

#### **Attack Payload:**

```sql
Username: sqli-test','','','');DELETE FROM mainapp_customer;--
Email: test@test.com
Password: Anything123!
```

---

### **🎯 Attack 3: Data Manipulation**

# mainapp/views.py - add_customer() function

#### **Attack Payload:**

```sql
First Name: TEST
Last Name: TEST
ID: 123','');DELETE FROM mainapp_customer;--
```
---

## 🚨 **XSS Attack Demonstrations**

### **🎯 Stored XSS Attack: Customer List**

# mainapp/views.py - add_customer() function

#### **Attack Payload:**

```html
First Name: TESTXSS
Last Name: TESTXSS
ID: <script> alert("XSS") </script>
```

#### **What Happens:**
1. Malicious script stored in database
2. Every user viewing customer list executes the script
3. **Persistent attack** affects all users

---

## 📖 **Detailed Setup**

### **🔧 Prerequisites**
- **Python 3.8+**
- **Django 5.2**
- **SQLite** (included)
- **Ethical Use Agreement** ⚖️

---

## 📚 **Vulnerability Documentation**

### **🔗 Vulnerable Endpoints**

| Method | Endpoint | Vulnerability | Attack Vector |
|--------|----------|---------------|---------------|
| `POST` | `/login/` | SQL Injection | Authentication bypass |
| `POST` | `/register/` | SQL Injection | Data destruction |
| `POST` | `/add_customer/` | SQL Injection + XSS | Data manipulation + script injection |
| `GET` | `/customer_list/` | Stored XSS | Script execution for all users |
| `GET` | `/system/` | Stored XSS | Dashboard script execution |
| `POST` | `/forgot_password/` | Information Disclosure | Reset token exposure |
| `POST` | `/reset_password/` | SQL Injection | Account takeover |

---

## 🛠️ **Technology Stack**

### **🔧 Backend Technologies (Vulnerable Configuration)**
- **Django 5.2** - Web framework (security features disabled)
- **Python 3.8+** - Programming language
- **SQLite** - Database (vulnerable to injection)
- **Raw SQL Queries** - Direct string concatenation
- **No Input Validation** - Accepts malicious input

### **🎨 Frontend Technologies (Vulnerable Configuration)**
- **HTML5** - Markup
- **CSS3** - Styling
- **Django Templates** - Server-side rendering (XSS vulnerable)
- **`|safe` Filters** - Disables XSS protection

### **🚨 Dangerous Implementations**
- **cursor.execute()** - Raw SQL concatenation
- **cursor.executescript()** - Multiple SQL statements
- **`|safe` template filter** - Disables escaping
- **No html.escape()** - Missing input sanitization
- **No regex validation** - Accepts any characters

### **📧 Email Integration (Information Disclosure)**
- **django.core.mail** - Email functionality
- **Exposed reset codes** - Displayed in HTML
- **No token validation** - Predictable reset codes

---

## 🚀 **Deployment**

### **🌐 Local Development (Vulnerable Environment)**
```bash
# Run on different port to avoid conflicts with secure version
python manage.py runserver 8001
```

### **⚠️ Production Warning**
**NEVER DEPLOY THIS CODE TO PRODUCTION!**

This code contains intentional vulnerabilities and should only be used in isolated educational environments.

---
