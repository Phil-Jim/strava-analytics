from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)


class StravaRedirectMiddleware:
    """
    Middleware to redirect users to Strava authentication after successful social login
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Check if we need to redirect to Strava after social login
        if (request.session.get('redirect_to_strava_after_login') and 
            request.user.is_authenticated and 
            request.path == '/' and 
            response.status_code == 200):
            
            logger.info("Middleware triggering Strava redirect after social login")
            
            # Clear the session flag
            del request.session['redirect_to_strava_after_login']
            
            # Add success message
            messages.success(
                request, 
                "Welcome! Let's connect your Strava account to get your activity data."
            )
            
            # Redirect to Strava auth
            strava_url = reverse('strava_auth')
            logger.info(f"Middleware redirecting to: {strava_url}")
            return redirect(strava_url)
        
        return response