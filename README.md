# Django Order Management System

This is a Django-based web application for managing customer orders. Users can submit orders via a form, and the system notifies a warehouse via email. The warehouse can confirm orders either by clicking a confirmation link or replying with specific keywords in an email, which is processed by a Celery task to update order statuses and notify users.

## Features
- **Order Submission**: Users submit orders with customer details, product selection, quantity, and email via a form at `http://localhost:8000`.
- **Email Notifications**: 
  - Upon order submission, an email is sent to the warehouse with order details and a confirmation link.
  - Upon confirmation, the user receives a confirmation email.
- **Order Confirmation**:
  - Warehouse confirms orders by clicking a link (e.g., `http://localhost:8000/order/1/confirm/`) or replying with an email containing keywords like "order ready to dispatch" or "is ready" and the order number.
- **Background Processing**: A Celery task (`check_emails`) runs every 60 seconds to process warehouse email replies, update order statuses, and send user notifications.
- **Admin Panel**: View and manage orders at `http://localhost:8000/admin`.

## Prerequisites
- **Python**: 3.8 or higher
- **Email Account**: A working SMTP/IMAP-enabled email account (e.g., Gmail with App Password)
- **Dependencies**: Listed in `requirements.txt`

## Project Structure
```
order_management/
├── manage.py
├── order_management/
│   ├── __init__.py
│   ├── celery.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
├── orders/
│   ├── __init__.py
│   ├── management/
│   │   ├── __init__.py
│   │   ├── commands/
│   │       ├── __init__.py
│   │       ├── populate_products.py
│   ├── migrations/
│   │   ├── __init__.py
│   ├── models.py
│   ├── tasks.py
│   ├── urls.py
│   ├── views.py
├── templates/
│   ├── orders/
│       ├── order_form.html
├── requirements.txt
├── README.md
```

## Setup Instructions

1. **Clone the Repository** (if applicable):
   ```bash
   git clone <repository-url>
   cd order_management
   ```

2. **Create and Activate Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   Or manually:
   ```bash
   pip install django celery redis django-celery-beat
   ```

4. **Configure Email Settings**:
   - Open `order_management/settings.py` and update:
     ```python
     # Django settings
      SECRET_KEY=django-duumy-ff(-a&h%l&_oaet)y^t=3#xesb(##dfgsdgdfghdghsd
      DEBUG=True
      ALLOWED_HOSTS=127.0.0.1,localhost

      # Email settings
      EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
      EMAIL_HOST=smtp.gmail.com
      EMAIL_PORT=587
      EMAIL_USE_TLS=True
      EMAIL_HOST_USER=yourapp@gmail.com
      EMAIL_HOST_PASSWORD=your-app-password
      DEFAULT_FROM_EMAIL=yourapp@gmail.com
      WAREHOUSE_EMAIL=warehouse@yourcompany.com

      # Celery settings
      CELERY_BROKER_URL=redis://localhost:6379/0
      CELERY_RESULT_BACKEND=redis://localhost:6379/0
      CELERY_TIMEZONE=UTC
     ```
   - For Gmail, generate an App Password (Google Account > Security > 2-Step Verification > App Passwords).
   - Ensure IMAP is enabled (Gmail Settings > Forwarding and POP/IMAP).

5. **Apply Migrations and Populate Data**:
   ```bash
   cd order_management
   python manage.py makemigrations
   python manage.py migrate
   python manage.py populate_products
   ```

6. **Create Admin User (Optional)**:
   ```bash
   python manage.py createsuperuser
   ```

## Running the Application

1. **Start Celery Worker**:
   In a new terminal:
   ```bash
   cd order_management
   source venv/bin/activate  # Windows: venv\Scripts\activate
   celery -A order_management worker -l info --pool=solo
   ```

2. **Start Celery Beat**:
   In another terminal:
   ```bash
   cd order_management
   source venv/bin/activate
   celery -A order_management beat -l info
   ```

3. **Start Django Server**:
   ```bash
   cd order_management
   python manage.py runserver
   ```

4. **Access the Application**:
   - Order Form: `http://localhost:8000`
   - Admin Panel: `http://localhost:8000/admin` (log in with superuser credentials)

## Testing the Workflow

1. **Submit an Order**:
   - Go to `http://localhost:8000`.
   - Fill out the form (e.g., Customer Name: Jane Doe, Customer ID: CUST123, Quantity: 2, Product: Smartphone, User Email: jane.doe@example.com).
   - Submit and verify:
     - Browser shows: "Order placed successfully! Warehouse has been notified."
     - Admin panel shows order with Status: Order Placed.
     - `warehouse@yourcompany.com` receives an email (Subject: `New Order #1`).

2. **Confirm via Link**:
   - Open the warehouse email and click the confirmation link (e.g., `http://localhost:8000/order/1/confirm/`).
   - Verify:
     - Browser shows: "Order confirmed and user notified."
     - Admin panel shows Status: Confirmed.
     - `jane.doe@example.com` receives an email (Subject: `Order #1 Confirmed`).

3. **Confirm via Email Reply**:
   - Reply to the order email from `warehouse@yourcompany.com` with:
     - Subject: `Order No 1 is ready`
     - Body: Any text (e.g., "Ready for shipping").
   - Wait up to 60 seconds for Celery to process.
   - Verify:
     - Admin panel shows Status: Confirmed.
     - `jane.doe@example.com` receives the confirmation email.
     - Celery worker logs show:
       ```
       [INFO] Found confirmation email with subject: Order No 1 is ready
       [INFO] Updated order 1 to Confirmed
       [INFO] Sent confirmation email to jane.doe@example.com
       ```

## License
<----------------------------------------------------------------------------------------------------------------------------->