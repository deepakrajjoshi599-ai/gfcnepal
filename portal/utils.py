import random
import string

from django.core.mail import send_mail
from django.utils import timezone

from .models import AccessToken, TokenUsageLog


def generate_token():
    chars = string.ascii_uppercase + string.digits + "@#$!%*"
    while True:
        token = "".join(random.choices(chars, k=16))
        if (
            any(c.isupper() for c in token)
            and any(c.isdigit() for c in token)
            and any(c in "@#$!%*" for c in token)
        ):
            return token


def create_token_for_email(email):
    return AccessToken.objects.create(token=generate_token(), email=email.lower().strip())


def send_token_email(access_token):
    subject = "GFC Nepal - New Access Token"
    message = f"Your one-time Codepass/Token is: {access_token.token}"
    send_mail(subject, message, None, [access_token.email], fail_silently=True)


def consume_token(token, email, user, ip_address):
    token = (token or "").strip()
    email = (email or "").strip().lower()
    try:
        access_token = AccessToken.objects.get(token=token)
    except AccessToken.DoesNotExist:
        return False, "Token भेटिएन।"
    if access_token.used:
        return False, "Token पहिले नै प्रयोग भइसकेको छ।"
    if access_token.email.lower() != email:
        return False, "यो token यो email को लागि होइन।"

    access_token.used = True
    access_token.used_by = user
    access_token.used_ip = ip_address or None
    access_token.used_at = timezone.now()
    access_token.save(update_fields=["used", "used_by", "used_ip", "used_at"])
    TokenUsageLog.objects.create(
        access_token=access_token,
        token=access_token.token,
        email=access_token.email,
        used_by=user,
        ip_address=ip_address or None,
    )

    new_token = create_token_for_email(access_token.email)
    send_token_email(new_token)
    return True, "Token valid। नयाँ token auto-generate भयो।"
