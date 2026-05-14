# OTP Email Configuration Guide

## Overview
The application now sends OTP (One-Time Password) emails to users during registration using Gmail SMTP.

## Setup Steps

### 1. Get Gmail Credentials

#### Step 1: Enable 2-Step Verification
1. Go to [myaccount.google.com](https://myaccount.google.com)
2. Click **Security** in the left sidebar
3. Enable **2-Step Verification** (if not already enabled)
4. Follow the prompts

#### Step 2: Generate App Password
1. Go back to **Security** page
2. Scroll down to **App passwords**
3. Select:
   - **Select app**: Mail
   - **Select device**: Linux (or your OS)
4. Click **Generate**
5. Google will display a 16-character password
6. **Copy and save this password** (you'll need it in Step 2)

### 2. Update Environment Variables

Edit your `.env` file:

```bash
# Gmail SMTP Configuration
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
```

Replace:
- `your-email@gmail.com` with your Gmail address
- `xxxx xxxx xxxx xxxx` with the 16-character app password

### 3. Test It

Register a new user via the API:

```bash
curl -X POST http://localhost:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "password123"
  }'
```

You should receive an OTP email at `test@example.com` with a beautiful HTML template containing the 6-digit code.

## Email Flow

### Registration Process
```
1. User POST /users/register
   ↓
2. Validate email & username uniqueness
   ↓
3. Create user account (hashed password)
   ↓
4. Generate random 6-digit OTP (expires in 5 minutes)
   ↓
5. Send OTP via Gmail SMTP
   ↓
6. Return user details (if email sent successfully)
```

### Email Template Features
- **Professional HTML design** - Clean, branded layout
- **Large OTP display** - 6-digit code is prominent and easy to read
- **Security notices** - Warns not to share OTP
- **Expiration info** - Shows 5-minute validity period
- **Responsive design** - Works on mobile and desktop

## How It Works

### 1. OTP Generation (`app/crud.py`)
```python
otp = str(random.randint(100000, 999999))  # 6-digit code
expires_at = datetime.utcnow() + timedelta(minutes=5)  # 5 min expiry
```

### 2. Email Sending (`app/email.py`)
- Uses Gmail SMTP server: `smtp.gmail.com:465`
- TLS/SSL encryption
- Authenticates with Gmail app password
- Sends HTML-formatted email

### 3. Error Handling
If email fails to send:
- Returns 500 error with message "Failed to send OTP email"
- Check logs for specific error
- Common issues:
  - Invalid Gmail credentials
  - Gmail account security settings
  - Network connectivity

## OTP Database

OTPs are stored in the `email_otps` table:

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| user_id | Integer | Foreign key to users table |
| otp | String | 6-digit code |
| expires_at | DateTime | Expiration timestamp |
| created_at | DateTime | When OTP was created |

## Troubleshooting

### "Gmail authentication failed"
- Check GMAIL_EMAIL is correct
- Verify GMAIL_APP_PASSWORD is correct (16 characters)
- Ensure 2-Step Verification is enabled on Google Account

### "SMTP connection error"
- Check internet connectivity
- Verify Gmail SMTP server is accessible
- Check firewall settings (port 465 must be open)

### "Failed to send OTP email"
- Check .env file has both GMAIL_EMAIL and GMAIL_APP_PASSWORD
- Verify credentials in .env are correct
- Check application logs for detailed error

### Email not received
- Check spam/junk folder
- Verify recipient email address is correct
- Wait up to 1 minute (emails may be delayed)
- Check Gmail quotas/limits (Gmail allows ~2000 emails/day)

## Future Enhancements

### To Add Later:
1. **OTP Verification Endpoint** - Endpoint to verify OTP and activate email
2. **Resend OTP Endpoint** - Allow users to request new OTP
3. **Email Templates** - Customizable, stored in database
4. **Rate Limiting** - Prevent spam email requests
5. **Email Queue** - Async email sending with background tasks (Celery)
6. **Email Analytics** - Track sent, opened, failed emails
7. **Multiple Email Services** - Support SendGrid, Mailgun, AWS SES
8. **Email Scheduling** - Schedule emails for later delivery

## Security Considerations

1. **App Password vs Account Password**
   - Always use App Password (more secure)
   - Never commit real passwords to git
   - Use environment variables

2. **OTP Security**
   - 6-digit code provides ~1 million combinations
   - 5-minute expiration prevents brute force
   - OTP is generated randomly (not sequential)

3. **Email Security**
   - TLS/SSL encryption with Gmail
   - HTML email includes security warnings
   - User told not to share OTP

4. **Rate Limiting**
   - Consider adding rate limits to prevent:
     - Spam registration attempts
     - Email flooding
     - Brute force OTP guessing

## Environment Variables Reference

| Variable | Example | Required | Purpose |
|----------|---------|----------|---------|
| GMAIL_EMAIL | your-email@gmail.com | Yes | Gmail address for sending |
| GMAIL_APP_PASSWORD | xxxx xxxx xxxx xxxx | Yes | 16-char Gmail app password |

## API Examples

### Register with OTP
```bash
curl -X POST http://localhost:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "username": "johndoe",
    "password": "SecurePass123"
  }'
```

**Success Response (201):**
```json
{
  "id": 1,
  "email": "john@example.com",
  "username": "johndoe",
  "is_active": true,
  "created_at": "2026-05-14T17:31:00"
}
```

**Email Received:**
```
To: john@example.com
Subject: Your Email Verification OTP

[Beautiful HTML email with 6-digit OTP]
```

## Logs

Monitor application logs for email sending:

```
INFO:app.email:OTP email sent successfully to john@example.com
ERROR:app.email:Gmail authentication failed. Check email/password.
```

To view logs in development:
```bash
# Run with verbose logging
uvicorn app.main:app --reload --log-level debug
```
