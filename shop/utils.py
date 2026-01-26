import random
import string
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta


def generate_otp(length=6):
    """Generate a random OTP of specified length."""
    return ''.join(random.choices(string.digits, k=length))


def send_verification_email(email, otp):
    """
    Send verification OTP to the given email address.
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        subject = 'GiftWorld - Email Verification OTP'
        message = f'''
Hello,

Your OTP for email verification is: {otp}

This OTP is valid for 10 minutes. Please do not share it with anyone.

If you didn't request this verification, please ignore this email.

Best regards,
GiftWorld Team
'''
        html_message = f'''
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #6B0F1A, #A91D3A); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
        .otp {{ font-size: 32px; font-weight: bold; color: #A91D3A; background: #fff; padding: 15px 30px; border-radius: 8px; display: inline-block; letter-spacing: 5px; margin: 20px 0; }}
        .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎁 GiftWorld</h1>
            <p>Email Verification</p>
        </div>
        <div class="content">
            <p>Hello,</p>
            <p>Your OTP for email verification is:</p>
            <div style="text-align: center;">
                <span class="otp">{otp}</span>
            </div>
            <p>This OTP is valid for <strong>10 minutes</strong>. Please do not share it with anyone.</p>
            <p>If you didn't request this verification, please ignore this email.</p>
            <div class="footer">
                <p>Best regards,<br>GiftWorld Team</p>
            </div>
        </div>
    </div>
</body>
</html>
'''
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Email Verification Error: {e}")
        return False


def verify_email_otp(session_otp, session_expiry, entered_otp):
    """
    Verify the entered OTP against the stored session OTP.
    Args:
        session_otp: OTP stored in session
        session_expiry: Expiry timestamp stored in session
        entered_otp: OTP entered by user
    Returns:
        bool: True if OTP is valid and not expired, False otherwise
    """
    if not session_otp or not session_expiry:
        return False
    
    # Check if OTP is expired
    try:
        expiry_time = datetime.fromisoformat(session_expiry)
        if datetime.now() > expiry_time:
            return False
    except (ValueError, TypeError):
        return False
    
    # Check if OTP matches
    return str(session_otp) == str(entered_otp)
