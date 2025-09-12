from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
import requests
import os
from datetime import datetime, timezone as dt_timezone
from django.utils import timezone
from .models import StravaProfile

def login_view(request):
    """Login page"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'activities/login.html')

def logout_view(request):
    """Logout user"""
    logout(request)
    return redirect('login')

def register_view(request):
    """Registration page"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'activities/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'activities/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'activities/register.html')
        
        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, 'Account created successfully! Please connect your Strava account.')
        
        # Log in the user
        login(request, user)
        
        # Redirect to Strava OAuth
        return redirect('strava_auth')
    
    return render(request, 'activities/register.html')

def strava_auth(request):
    """Initiate Strava OAuth flow"""
    client_id = os.getenv('STRAVA_CLIENT_ID')
    redirect_uri = request.build_absolute_uri(reverse('strava_callback'))
    
    strava_auth_url = (
        f"https://www.strava.com/oauth/authorize?"
        f"client_id={client_id}&"
        f"response_type=code&"
        f"redirect_uri={redirect_uri}&"
        f"approval_prompt=force&"
        f"scope=read,activity:read_all"
    )
    
    return redirect(strava_auth_url)

def strava_callback(request):
    """Handle Strava OAuth callback"""
    code = request.GET.get('code')
    error = request.GET.get('error')
    
    if error:
        messages.error(request, f'Strava authorization failed: {error}')
        return redirect('dashboard')
    
    if not code:
        messages.error(request, 'No authorization code received from Strava.')
        return redirect('dashboard')
    
    # Exchange code for tokens
    client_id = os.getenv('STRAVA_CLIENT_ID')
    client_secret = os.getenv('STRAVA_CLIENT_SECRET')
    
    token_url = "https://www.strava.com/oauth/token"
    token_data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code,
        'grant_type': 'authorization_code'
    }
    
    try:
        response = requests.post(token_url, data=token_data)
        response.raise_for_status()
        token_info = response.json()
        
        # Save or update user's Strava profile
        strava_profile, created = StravaProfile.objects.update_or_create(
            user=request.user,
            defaults={
                'strava_user_id': token_info['athlete']['id'],
                'access_token': token_info['access_token'],
                'refresh_token': token_info['refresh_token'],
                'expires_at': datetime.fromtimestamp(token_info['expires_at'], tz=dt_timezone.utc)
            }
        )
        
        messages.success(request, 'Strava account connected successfully!')
        
        # Start syncing activities
        return redirect('sync_activities')
        
    except requests.RequestException as e:
        messages.error(request, f'Failed to connect to Strava: {str(e)}')
        return redirect('dashboard')

def sync_activities_view(request):
    """Trigger activity sync for current user"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        strava_profile = request.user.strava_profile
    except StravaProfile.DoesNotExist:
        messages.error(request, 'Please connect your Strava account first.')
        return redirect('strava_auth')
    
    # Import here to avoid circular imports
    from .strava_service import StravaService
    
    try:
        service = StravaService(strava_profile)
        activities_synced = service.sync_all_activities()
        messages.success(request, f'Synced {activities_synced} activities from Strava!')
    except Exception as e:
        messages.error(request, f'Failed to sync activities: {str(e)}')
    
    return redirect('dashboard')