# GeminiBackend

A Django REST API backend for chatroom management, OTP-based authentication, Stripe-powered subscriptions, and Google Gemini integration.

## Features
- OTP-based user authentication (mobile number only)
- JWT authentication for protected routes
- Chatroom creation, listing, messaging (with async Gemini API integration ready)
- Stripe subscription management (Basic/Pro tiers)
- Rate limiting for Basic users
- Caching for chatroom list endpoint
- Consistent JSON responses and robust middleware

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd GeminiBackend
```

### 2. Create and Activate Virtual Environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
- Copy `env.example` to `.env` and fill in your secrets and config:
```bash
cp gemini_backend/env.example gemini_backend/.env
```
- Edit `.env` as needed (see comments in the file).

### 5. Database Setup
- By default, uses SQLite. For PostgreSQL, set `DATABASE_URL` in `.env` and ensure PostgreSQL is running.
- Run migrations:
```bash
python manage.py migrate
```

### 6. Run the Server
```bash
python manage.py runserver
```

## API Documentation
- All endpoints are organized and described in the included Postman collection: `GeminiBackend.postman_collection.json`.
- Import this file into Postman for ready-to-use, folder-structured requests.
- JWT tokens are handled automatically in the collection.

## Main Endpoints
- `/auth/signup`, `/auth/send-otp`, `/auth/verify-otp`, `/auth/forgot-password`, `/auth/change-password`, `/auth/user/me`
- `/chatroom/`, `/chatroom/:id/`, `/chatroom/:id/message/`
- `/subscribe/pro`, `/subscription/status`, `/webhook/stripe`

## Environment Variables
See `env.example` for all required and optional variables (Django, Stripe, DB, Email, JWT, Celery, etc).

## Notes
- Caching is used for chatroom listing and usage tracking.
- Rate limiting is enforced for Basic users (5 messages/day).
- Stripe is used in test mode by default.
- Async Gemini API integration is ready for Celery/worker setup.

---

**For any issues or questions, please refer to the code comments or contact the maintainer.** 