# aamarPay Django Task – Abdul Monim
A Django REST Framework project that integrates **aamarPay sandbox payments**, **file uploads**, and **Celery-based asynchronous word counting**.

Features:
- Django + DRF API endpoints
- aamarPay payment integration (sandbox)
- File uploads (.txt and .docx) after successful payment
- Word count processing via Celery + Redis
- Activity logging
- Bootstrap dashboard for file management
- Local and Docker support

---

## **Setup Instructions**

### **1. Clone the repo**
git clone https://github.com/<your-username>/aamarPay-django-task-abdul-monim.git
cd aamarPay-django-task-abdul-monim
## 2. Local Development Setup
**Prerequisites**:
- Python 3.12+
- Redis (local server on port 6379)
**Install dependencies**
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
**Create a .env in the same folder as manage.py**
SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=*
STORE_ID=aamarpaytest
SIGNATURE_KEY=dbb74894e82415a2f7ff0ec3a97e4183
AAMARPAY_ENDPOINT=https://sandbox.aamarpay.com/jsonpost.php
AAMARPAY_TRX_CHECK=https://sandbox.aamarpay.com/api/v1/trxcheck/request.php
MEDIA_URL=/media/
## Run database migration
python manage.py migrate
python manage.py createsuperuser
## Run the services
**Terminal 1 (Django server)**:
python manage.py runserver
**Terminal 2 (Celery worker)**:
celery -A aamarpay_project worker --loglevel=info
## Celery & Redis Setup
**Local:** Install Redis and run:
redis-server
celery -A aamarpay_project worker --loglevel=info
**Docker:** Already included as a service in docker-compose.yml:

## 3. Docker Setup
docker compose up --build

## 4. API Usage Examples
**🛠 API Testing with Postman**

**You can quickly import all API endpoints into Postman by clicking the button below:**

[![Run in Postman](https://run.pstmn.io/button.svg)](https://god.postman.co/run-collection?source=raw.githubusercontent.com/Monim752/aamarPay-django-task-abdul-monim/main/docs/aamarpay_postman_collection.json)
