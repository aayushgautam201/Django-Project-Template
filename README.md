# 🔩 Django Project Template

A production-ready Django project template with robust authentication features, email and OTP verification, password management, and a modular API-ready structure using Django REST Framework.

---

## ✨ Features

* ✅ User Signup with Email Verification
* 🔐 JWT Authentication (Login/Refresh)
* 🔁 Password Reset via Email
* 📟 Change Password (Logged-in users)
* 🔢 OTP Verification (Signup / Password Reset)
* 📬 Custom Email Service Integration
* 🌐 API-Ready with Django REST Framework
* ⚙️ Environment-based Settings Support
* 🔒 CORS, CSRF, and Security Configurations
* 🔜 Social Login (Coming Soon)

---

## 🚀 Getting Started

Follow these steps to set up the project locally:

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/aayushgautam201/Django-Project-Template.git
cd Django-Project-Template
```

---

### 2️⃣ Set Up a Virtual Environment

```bash
# For Linux/macOS
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
venv\Scripts\activate
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Configure Environment Variables

Update your `.env` file with appropriate values:

```env
SECRET_KEY=your_secret_key
DEBUG=True

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_email_password
```

---

### 5️⃣ Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

### 6️⃣ Create a Superuser

```bash
python manage.py createsuperuser
```

---

### 7️⃣ Run the Development Server

```bash
python manage.py runserver
```

Visit: [http://127.0.0.1:8000](http://127.0.0.1:8000)


## ⚙️ Technologies Used

* Python 3.10+
* Django 4+
* Django REST Framework
* JWT Authentication (`djangorestframework-simplejwt`)
* PostgreSQL / MySQL Compatible
* SMTP Email Service
* Python dotenv

---

## 🧪 Testing the API

You can test the endpoints using:

* [Postman](https://www.postman.com/)
* [cURL](https://curl.se/)
* Any frontend/mobile client

## 🤛👨‍💼 Author

Made with ❤️ by [Aayush Gautam](https://github.com/aayushgautam201)
