# User API Documentation

## Overview
FastAPI-based user management system with JWT authentication and PostgreSQL database.

## Features
- **User Registration**: Create new user accounts
- **User Login**: Authenticate users with email/password
- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: Bcrypt for secure password storage
- **User Profile**: Retrieve current user information

## Setup

### Prerequisites
- Python 3.8+
- PostgreSQL database

### Installation

1. **Clone the repository**
   ```bash
   cd project_001-DEMO
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Update .env with your PostgreSQL credentials
   ```

5. **Run the server**
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`

## API Endpoints

### 1. Register User
**POST** `/users/register`

**Request Body:**
```json
{
  "email": "user@example.com",
  "username": "john_doe",
  "password": "securepassword123"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "john_doe",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00"
}
```

### 2. Login User
**POST** `/users/login`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "username": "john_doe",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00"
  }
}
```

### 3. Get Current User
**GET** `/users/me`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "john_doe",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Email already registered"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid email or password"
}
```

### 404 Not Found
```json
{
  "detail": "User not found"
}
```

## Testing with cURL

```bash
# Register a user
curl -X POST http://localhost:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"password123"}'

# Login
curl -X POST http://localhost:8000/users/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Get current user (replace TOKEN with actual token)
curl -X GET http://localhost:8000/users/me \
  -H "Authorization: Bearer TOKEN"
```

## Interactive API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Database Schema

### Users Table
```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR UNIQUE NOT NULL,
  username VARCHAR UNIQUE NOT NULL,
  hashed_password VARCHAR NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Environment Variables

See `.env.example` for configuration options:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT signing key (change in production!)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time

## Security Notes

1. **Change SECRET_KEY in production** - Use a strong, random key
2. **Use HTTPS in production** - Never transmit tokens over plain HTTP
3. **Implement rate limiting** - Prevent brute force attacks
4. **Add email verification** - Confirm user email addresses
5. **Add password reset functionality** - For user convenience

## File Structure

```
app/
├── main.py          # FastAPI application
├── config.py        # Configuration settings
├── models.py        # SQLAlchemy models
├── schemas.py       # Pydantic schemas
├── database.py      # Database connection
├── security.py      # JWT and password utilities
├── crud.py          # Database operations
└── routers.py       # API endpoints
```
