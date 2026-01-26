# GiftWorld - Django Gift Shop

A full-featured e-commerce gift shop built with Django, featuring database storage, file uploads, and Razorpay payment integration.

## Features

- 🎁 **Product Catalog**: Categories, products with images, badges, and pricing
- 🛒 **Shopping Cart**: Session-based cart with add, update, and remove functionality
- 💳 **Payment Gateway**: Razorpay integration for secure payments
- 📱 **Responsive Design**: Mobile-friendly interface
- 🔐 **Admin Dashboard**: Full Django admin for managing products, orders, and customers
- 📦 **Order Management**: Complete order lifecycle with status tracking
- 💬 **Contact Form**: Customer enquiry submission
- 📸 **Media Storage**: Image uploads for products and testimonials

## Tech Stack

- **Backend**: Django 4.2+
- **Database**: SQLite (development) / PostgreSQL (production)
- **Payment**: Razorpay
- **Frontend**: HTML, CSS, JavaScript
- **Icons**: Font Awesome

## Installation

1. **Clone the repository**
   ```bash
   cd GiftWorld
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create sample data** (optional)
   ```bash
   python create_sample_data.py
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the site**
   - Website: http://127.0.0.1:8000/
   - Admin: http://127.0.0.1:8000/admin/

## Razorpay Setup

1. Create an account at [Razorpay Dashboard](https://dashboard.razorpay.com/)
2. Get your API keys from Settings > API Keys
3. Update `giftworld_project/settings.py`:
   ```python
   RAZORPAY_KEY_ID = 'your_key_id'
   RAZORPAY_KEY_SECRET = 'your_key_secret'
   ```

   Or set environment variables:
   ```bash
   set RAZORPAY_KEY_ID=your_key_id
   set RAZORPAY_KEY_SECRET=your_key_secret
   ```

## Project Structure

```
GiftWorld/
├── giftworld_project/     # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── shop/                  # Main shop app
│   ├── models.py          # Product, Category, Order models
│   ├── views.py           # Shop views
│   ├── urls.py            # Shop URLs
│   └── admin.py           # Admin configuration
├── payments/              # Payment app
│   ├── models.py          # Payment models
│   └── views.py           # Razorpay integration
├── templates/             # HTML templates
│   ├── base.html
│   └── shop/
├── static/                # Static files (CSS, JS)
├── media/                 # Uploaded files
└── manage.py
```

## Admin Credentials (if using sample data)

- **Username**: admin
- **Password**: admin123

⚠️ **Change these credentials in production!**

## Models

### Category
- name, slug, description, image

### Product
- name, category, description, price, discount_price, image, badge, stock

### Order
- order_id, customer, items, status, payment_status, razorpay details

### Customer
- name, email, phone, address

### Testimonial
- customer_name, content, rating, occasion

## API Endpoints

- `GET /` - Home page
- `GET /shop/` - Product listing with filters
- `GET /product/<slug>/` - Product detail
- `GET /cart/` - Shopping cart
- `POST /cart/add/` - Add to cart (AJAX)
- `POST /cart/update/` - Update cart (AJAX)
- `GET /checkout/` - Checkout page
- `POST /payments/create-order/` - Create Razorpay order
- `POST /payments/verify/` - Verify payment

## License

MIT License - feel free to use for personal or commercial projects.

## Contact

GiftWorld, Chitravani Road, Bhatta Bazar, Purnea, Bihar 854301
Phone: +91 7542043169
Email: giftworldonlineofficial@gmail.com
