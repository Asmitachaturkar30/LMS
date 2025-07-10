from django.core.mail import send_mail
from django.conf import settings
import random
import string
import re
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


# --- Email Notifications ---

from django.core.mail import send_mail

def send_login_success_email(email):
    subject = "Successful Login Notification"
    message = f"""
        Hello,

        You have successfully logged in to your account.

        Details:
        - Email: {email}

        If this wasn't you, please secure your account immediately.

        Regards,
        Your App Team
    """
    result = send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False
    )
    return result  # Returns number of successfully delivered messages (1 if successful)

# --- OTP Generation ---

def generate_otp(length=6):
    """
    Generate a random OTP (One Time Password) of a specified length.
    """
    return ''.join(random.choices(string.digits, k=length))

# --- OTP Email Notification ---

def send_otp_email(email, otp):
    subject = "Your OTP for Password Reset"
    message = f"Your OTP for password reset is: {otp}\nThis OTP is valid for 5 minutes."

    try:
        from_email = settings.DEFAULT_FROM_EMAIL
        if not from_email:
            raise ImproperlyConfigured("DEFAULT_FROM_EMAIL is not set in settings.py")

        send_mail(subject, message, from_email, [email])
        return True

    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False




def is_strong_password(password):
    return (
        len(password) >= 8 and
        re.search(r'[A-Z]', password) and
        re.search(r'[a-z]', password) and
        re.search(r'[0-9]', password) and
        re.search(r'[\W_]', password)
    )

# --- Helper Functions ---

def get_user_log_details(request):
    """
    Fetch client IP address and user agent from the request, considering proxy headers.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')

    # Use the first IP address if it's a proxy, else get the direct IP
    ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.META.get('REMOTE_ADDR')
    return ip, user_agent




# utils.py (optional utility file)
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')
