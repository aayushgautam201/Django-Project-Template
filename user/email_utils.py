from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

# Company email constants
COMPANY_NAME = "Your Company Name"
SUPPORT_EMAIL = "Support Email"
COMPANY_WEBSITE = "Webstite URL"
COMPANY_ADDRESS = "Your Company Address"
COPYRIGHT_YEAR = "copyright "

def send_dynamic_email(email_type, to_email, data, request=None):
    """
    Send a dynamic email based on the email type.

    Args:
        email_type (str): Type of email ('registration', 'forgot_password', 'user_verification')
        to_email (list): List of recipient email addresses
        data (dict): Data specific to the email type (e.g., user, otp)
        request (HttpRequest, optional): Request object for generating absolute URLs (for forgot_password or user_verification)

    Returns:
        bool: True if email sent successfully, False otherwise
    """
    # Initialize context with company constants
    context = {
        'closing_message': f'If you have any questions, please contact us at {SUPPORT_EMAIL}.',
        'signature_message': f'Best regards, The {COMPANY_NAME} Team',
        'company_name': COMPANY_NAME,
        'company_website': COMPANY_WEBSITE,
        'company_address': COMPANY_ADDRESS,
        'copyright_year': COPYRIGHT_YEAR
    }
    subject = ''
    user_name = f"{data.get('user').first_name} {data.get('user').last_name}" if data.get('user') else 'Customer'

    # Set context and subject based on email_type
    if email_type == 'registration':
        subject = f'Welcome to {COMPANY_NAME}!'
        context.update({
            'email_title': f'Welcome to {COMPANY_NAME}',
            'user_name': user_name,
            'main_message': f"Thank you for registering with {COMPANY_NAME}! We're excited to have you on board. Please verify your account using the OTP sent in a separate email.",
            'closing_message': 'Explore our services and book your next stay with us!',
        })

    elif email_type == 'user_verification':
        otp = data.get('otp', '123456')  # Default for testing; replace with actual OTP
        subject = f'Verify Your {COMPANY_NAME} Account'
        context.update({
            'email_title': 'Account Verification',
            'user_name': user_name,
            'main_message': f'Please verify your {COMPANY_NAME} account using the OTP below to activate your account.',
            'user_verification': True,
            'otp': otp,
            'closing_message': f'If you didn’t request this, please ignore this email or contact us at {SUPPORT_EMAIL}.',
        })

    elif email_type == 'forgot_password':
        otp = data.get('otp', '123456')  # Default for testing; replace with actual OTP
        subject = 'Password Reset OTP'
        context.update({
            'email_title': 'Password Reset OTP',
            'user_name': user_name,
            'main_message': 'We received a request to reset your password. Please use the OTP below to reset your password.',
            'reset_password': True,
            'otp': otp,
            'closing_message': f'If you didn’t request this, please ignore this email or contact us at {SUPPORT_EMAIL}.',
        })

    else:
        raise ValueError(f"Invalid email_type: {email_type}")

    # Render HTML content
    html_content = render_to_string('emails/email_template.html', context)
    
    # Create plain text fallback
    text_content = f"Hello {context['user_name']},\n\n{context['main_message']}\n\n{context['closing_message']}\n\n{context['signature_message']}"
    
    # Create email
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=to_email
    )
    email.attach_alternative(html_content, "text/html")
    
    # Send email
    try:
        email.send()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False