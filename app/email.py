import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import GMAIL_EMAIL, GMAIL_APP_PASSWORD
import logging

logger = logging.getLogger(__name__)

def send_otp_email(to_email: str, otp: str, username: str) -> bool:
    """
    Send OTP to user's email via Gmail SMTP.
    
    Args:
        to_email: Recipient email address
        otp: One-time password (6 digits)
        username: User's username for personalization
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Email content
        subject = "Your Email Verification OTP"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .header {{ text-align: center; color: #333; margin-bottom: 20px; }}
                .otp-box {{ background-color: #f0f0f0; padding: 20px; text-align: center; margin: 20px 0; border-radius: 8px; border: 2px solid #007bff; }}
                .otp-text {{ font-size: 32px; font-weight: bold; color: #007bff; letter-spacing: 5px; }}
                .message {{ color: #666; margin: 15px 0; line-height: 1.6; }}
                .footer {{ color: #999; font-size: 12px; text-align: center; margin-top: 20px; border-top: 1px solid #eee; padding-top: 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Email Verification</h1>
                </div>
                
                <p class="message">Hi <strong>{username}</strong>,</p>
                
                <p class="message">
                    Thank you for signing up! To verify your email address, please use the following One-Time Password (OTP):
                </p>
                
                <div class="otp-box">
                    <div class="otp-text">{otp}</div>
                </div>
                
                <p class="message">
                    This OTP is valid for <strong>5 minutes</strong>. If you did not request this code, please ignore this email.
                </p>
                
                <p class="message">
                    Do not share this OTP with anyone. Our team will never ask for your OTP.
                </p>
                
                <div class="footer">
                    <p>This is an automated message. Please do not reply to this email.</p>
                    <p>&copy; 2026 Your Application. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Create message
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = GMAIL_EMAIL
        message["To"] = to_email
        
        # Attach HTML body
        message.attach(MIMEText(html_body, "html"))
        
        # Send email via Gmail SMTP
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_EMAIL, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_EMAIL, to_email, message.as_string())
        
        logger.info(f"OTP email sent successfully to {to_email}")
        return True
        
    except smtplib.SMTPAuthenticationError:
        logger.error(f"Gmail authentication failed. Check email/password.")
        return False
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error occurred: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error sending OTP email: {str(e)}")
        return False
