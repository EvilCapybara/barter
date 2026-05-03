🔄 Item Exchange Web App (Django)

A Django-based web application for exchanging items between users through structured trade proposals.

This project demonstrates relational data modeling, server-side validation, filtering, pagination, and user-driven workflows using Django.

✨ Features
📦 Create and manage item listings (ads)
🔄 Send exchange proposals between items
✅ Accept or reject incoming offers
⏳ Track proposal status (pending / accepted / rejected)
🔍 Filter offers by sender, receiver, and status
📄 Paginated lists of sent and received offers
🔐 Authentication-based access control
🧪 Basic test coverage for core functionality
🧠 Architecture Overview

The project is structured around standard Django layers.

Views Layer (views.py):
Handles HTTP requests, processes forms, applies filtering and pagination, and enforces business rules such as ownership and validation.

Models Layer (models.py):
Defines User (custom user model), Ad (item listing), and ExchangeProposal (trade offer between two ads). Handles relationships, status logic via TextChoices, and data integrity.

Forms Layer (forms.py):
Provides validation, secure input handling, and ModelForm integration.

Templates Layer (templates/):
Responsible for rendering UI, displaying offers and ads, handling filtering and pagination, and user interactions.

📁 Project Structure

barter/
├── barter/
│ ├── asgi.py
│ ├── settings.py
│ ├── urls.py
│ ├── views.py
│ ├── wsgi.py
│ ├── tests.py
├── exchanges/
│ ├── migrations/
│ ├── admin.py
│ ├── apps.py
│ ├── forms.py
│ ├── models.py
│ ├── views.py
│ ├── tests.py
├── templates/
├── users/
├── ads/
├── manage.py
├── requirements.txt
└── README.md

⚙️ Requirements
Python 3.8+
Django 4.x
pip
🚀 Installation
Clone the repository:
git clone <repository_url>
cd exchange_app
Create a virtual environment:
python -m venv venv
source venv/bin/activate (Windows: venv\Scripts\activate)
Install dependencies:
pip install -r requirements.txt
⚙️ Database Setup

Apply migrations:
python manage.py makemigrations
python manage.py migrate

(Optional) Create superuser:
python manage.py createsuperuser

▶️ Running the Application

python manage.py runserver

Open in browser:
http://127.0.0.1:8000/

🔄 Core Workflow
User creates ads (items)
User sends an exchange proposal:
ad_sender_id — their item
ad_receiver_id — target item
Receiver can accept or reject the proposal
Status updates automatically
🔍 Filtering & Pagination

Users can filter exchange proposals by sender (username), receiver (username), and status (pending / accepted / rejected).

Results are paginated separately for sent and received proposals.

🧪 Running Tests

python manage.py test

Tests cover ad creation, exchange proposal creation, filtering logic, and validation.

🧩 Technical Highlights
Django ORM with relational integrity
Custom user model
TextChoices for status handling
Server-side validation (including protection against fake POST requests)
Separate logic for sent and received offers
Independent pagination
Clear separation of concerns
🛠 Future Improvements
REST API using Django REST Framework
Real-time notifications
Image upload support
Advanced filtering and search
UI improvements
Email notifications
Exchange history tracking
📄 License

This project is intended for educational use.
