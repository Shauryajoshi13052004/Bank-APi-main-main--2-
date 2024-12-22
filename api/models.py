from django.db import models
from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin
from django.dispatch import receiver

from api.manger import UserManager


from django.db.models.signals import post_save
from django.dispatch import receiver

from django.core.mail import send_mail
from django.conf import settings
from asgiref.sync import sync_to_async


class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    username = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

from asgiref.sync import sync_to_async
from django.core.mail import send_mail
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

# Get the custom user model
CustomUser = get_user_model()

# Async wrapper for the send_mail function
@sync_to_async
def send_email_sync(subject, message, recipient_list):
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

# Async signal handler
@receiver(post_save, sender=CustomUser)
async def send_email(sender, instance, created, **kwargs):
    if not created:  # Trigger on user updates
        if instance.is_verified:
            print('User verified')
            subject = 'Welcome to Our Platform'
            message = 'Congratulations! Your account has been successfully verified.'
            recipient_list = [instance.email]  # Use the user's email
            
            # Use async send_email_sync to send the email asynchronously
            await send_email_sync(subject, message, recipient_list)
            print('Verification email sent.')

        else:
            print('User not verified')
            subject = 'Account Verification Pending'
            message = (
                'Your account verification is pending. '
                'Please check your email for further instructions.'
            )
            recipient_list = [instance.email]  # Use the user's email
            
            # Use async send_email_sync to send the email asynchronously
            await send_email_sync(subject, message, recipient_list)
            print('Pending verification email sent.')
