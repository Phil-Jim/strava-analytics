from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialLogin
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
import logging

logger = logging.getLogger(__name__)


class StravaConnectSocialAdapter(DefaultSocialAccountAdapter):
    """
    Custom social account adapter that automatically initiates Strava connection
    after successful social login
    """
    
    def save_user(self, request, sociallogin, form=None):
        """
        Saves a newly signed up social login user
        """
        user = super().save_user(request, sociallogin, form)
        
        # Set username from social data if not provided
        if not user.username:
            # Try to get username from social data
            name = sociallogin.account.extra_data.get('name', '')
            first_name = sociallogin.account.extra_data.get('first_name', '')
            if name:
                user.username = name.replace(' ', '_').lower()
            elif first_name:
                user.username = first_name.lower()
            else:
                user.username = f"user_{user.id}"
            user.save()
            logger.info(f"Set username for new user: {user.username}")
        
        return user
    
    def get_login_redirect_url(self, request):
        """
        Returns the default URL to redirect to after logging in.
        Override to redirect to Strava connection.
        """
        logger.info("get_login_redirect_url called - redirecting to Strava auth")
        
        # Add a flag to the session to trigger Strava connection
        request.session['connect_strava_after_social_login'] = True
        
        # Add success message
        messages.success(
            request, 
            "Welcome! Let's connect your Strava account to get your activity data."
        )
        
        # Redirect to Strava auth
        strava_url = reverse('strava_auth')
        logger.info(f"Redirecting to: {strava_url}")
        return strava_url
    
    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user successfully authenticates via a
        social provider, but before the login is actually processed
        """
        logger.info(f"Pre-social login for provider: {sociallogin.account.provider}")
        logger.info(f"Extra data: {sociallogin.account.extra_data}")
        
        # Store Strava redirect flag in session IMMEDIATELY
        request.session['redirect_to_strava_after_login'] = True
        
        # Get the user's email from social account - try multiple fields since Facebook may not provide email
        email = (sociallogin.account.extra_data.get('email') or 
                sociallogin.email_addresses[0].email if sociallogin.email_addresses else None)
        
        if email:
            # Check if user with this email already exists
            try:
                existing_user = User.objects.get(email=email)
                # Connect the social account to existing user
                sociallogin.connect(request, existing_user)
                logger.info(f"Connected social account to existing user: {existing_user.email}")
            except User.DoesNotExist:
                # New user - will be created automatically
                logger.info("New user will be created")
        else:
            logger.info("No email found in social login")


class StravaConnectAccountAdapter:
    """
    Custom account adapter for regular login
    """
    
    def get_login_redirect_url(self, request):
        """
        Returns the default URL to redirect to after logging in.
        """
        return reverse('dashboard')