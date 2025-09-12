import requests
import time
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from .models import Activity, StravaProfile


class StravaService:
    """Service class to interact with Strava API"""
    
    BASE_URL = "https://www.strava.com/api/v3"
    
    def __init__(self, strava_profile=None):
        self.strava_profile = strava_profile
        if strava_profile:
            self.client_id = settings.STRAVA_CLIENT_ID
            self.client_secret = settings.STRAVA_CLIENT_SECRET
            self.access_token = strava_profile.access_token
            self.refresh_token = strava_profile.refresh_token
        else:
            # Fallback to environment variables for backward compatibility
            self.client_id = settings.STRAVA_CLIENT_ID
            self.client_secret = settings.STRAVA_CLIENT_SECRET
            self.access_token = settings.STRAVA_ACCESS_TOKEN
            self.refresh_token = settings.STRAVA_REFRESH_TOKEN
    
    def _make_request(self, endpoint, params=None):
        """Make a request to Strava API with error handling"""
        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 401:
                # Token expired, try to refresh
                if self.refresh_access_token():
                    # Retry with new token
                    headers['Authorization'] = f'Bearer {self.access_token}'
                    response = requests.get(url, headers=headers, params=params)
                else:
                    raise Exception("Failed to refresh access token")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {url}: {e}")
            raise
    
    def refresh_access_token(self):
        """Refresh the access token using refresh token"""
        url = "https://www.strava.com/oauth/token"
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'refresh_token': self.refresh_token,
            'grant_type': 'refresh_token'
        }
        
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            self.refresh_token = token_data['refresh_token']
            
            # You should update your .env file with new tokens
            print("Access token refreshed successfully")
            print(f"New access token: {self.access_token}")
            print(f"New refresh token: {self.refresh_token}")
            
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"Error refreshing access token: {e}")
            return False
    
    def get_athlete_info(self):
        """Get current athlete information"""
        return self._make_request("/athlete")
    
    def get_activities(self, page=1, per_page=200, after=None, before=None):
        """
        Fetch activities from Strava API
        
        Args:
            page: Page number (default 1)
            per_page: Number of activities per page (max 200)
            after: Unix timestamp to get activities after this date
            before: Unix timestamp to get activities before this date
        """
        params = {
            'page': page,
            'per_page': per_page
        }
        
        if after:
            params['after'] = after
        if before:
            params['before'] = before
        
        return self._make_request("/athlete/activities", params)
    
    def get_activity_details(self, activity_id):
        """Get detailed information for a specific activity"""
        return self._make_request(f"/activities/{activity_id}")
    
    def sync_all_activities(self, limit=None):
        """
        Sync all activities from Strava to local database
        
        Args:
            limit: Maximum number of activities to sync (None for all)
        """
        print("Starting activity sync...")
        
        page = 1
        per_page = 200
        total_synced = 0
        total_new = 0
        
        while True:
            print(f"Fetching page {page}...")
            
            try:
                activities = self.get_activities(page=page, per_page=per_page)
                
                if not activities:
                    print("No more activities found")
                    break
                
                for activity_data in activities:
                    if limit and total_synced >= limit:
                        break
                    
                    created = self.save_activity(activity_data)
                    if created:
                        total_new += 1
                    total_synced += 1
                
                print(f"Processed {len(activities)} activities from page {page}")
                
                if limit and total_synced >= limit:
                    break
                
                if len(activities) < per_page:
                    print("Reached end of activities")
                    break
                
                page += 1
                
                # Rate limiting - Strava allows 100 requests per 15 minutes
                time.sleep(0.2)
                
            except Exception as e:
                print(f"Error syncing activities: {e}")
                break
        
        print(f"Sync complete! Total processed: {total_synced}, New activities: {total_new}")
        return total_synced, total_new
    
    def save_activity(self, activity_data):
        """
        Save activity data to database
        
        Returns:
            bool: True if new activity was created, False if updated
        """
        strava_id = activity_data.get('id')
        
        # Convert start_date to datetime
        start_date_str = activity_data.get('start_date')
        if start_date_str.endswith('Z'):
            start_date_str = start_date_str[:-1] + '+00:00'
        start_date = datetime.fromisoformat(start_date_str)
        if start_date.tzinfo is None:
            start_date = timezone.make_aware(start_date)
        
        # Prepare activity data
        activity_fields = {
            'name': activity_data.get('name', ''),
            'activity_type': activity_data.get('type', 'Other'),
            'start_date': start_date,
            'distance': activity_data.get('distance', 0),
            'moving_time': activity_data.get('moving_time', 0),
            'elapsed_time': activity_data.get('elapsed_time', 0),
            'average_speed': activity_data.get('average_speed'),
            'max_speed': activity_data.get('max_speed'),
            'total_elevation_gain': activity_data.get('total_elevation_gain'),
            'average_heartrate': activity_data.get('average_heartrate'),
            'max_heartrate': activity_data.get('max_heartrate'),
            'average_watts': activity_data.get('average_watts'),
            'max_watts': activity_data.get('max_watts'),
            'calories': activity_data.get('calories'),
        }
        
        # Add user if we have a strava_profile
        if self.strava_profile:
            activity_fields['user'] = self.strava_profile.user
        
        # Handle start coordinates
        start_latlng = activity_data.get('start_latlng')
        if start_latlng and len(start_latlng) >= 2:
            activity_fields['start_latitude'] = start_latlng[0]
            activity_fields['start_longitude'] = start_latlng[1]
        
        # Handle end coordinates
        end_latlng = activity_data.get('end_latlng')
        if end_latlng and len(end_latlng) >= 2:
            activity_fields['end_latitude'] = end_latlng[0]
            activity_fields['end_longitude'] = end_latlng[1]
        
        # Create or update activity
        if self.strava_profile:
            activity, created = Activity.objects.update_or_create(
                user=self.strava_profile.user,
                strava_id=strava_id,
                defaults=activity_fields
            )
        else:
            # Fallback for backward compatibility 
            activity, created = Activity.objects.update_or_create(
                strava_id=strava_id,
                defaults=activity_fields
            )
        
        if created:
            print(f"Created new activity: {activity.name}")
        else:
            print(f"Updated activity: {activity.name}")
        
        return created
    
    def sync_recent_activities(self, days=7):
        """
        Sync activities from the last N days
        
        Args:
            days: Number of days to look back
        """
        from datetime import timedelta
        
        # Calculate timestamp for N days ago
        days_ago = timezone.now() - timedelta(days=days)
        after_timestamp = int(days_ago.timestamp())
        
        print(f"Syncing activities from last {days} days...")
        
        page = 1
        total_synced = 0
        total_new = 0
        
        while True:
            try:
                activities = self.get_activities(
                    page=page, 
                    per_page=200, 
                    after=after_timestamp
                )
                
                if not activities:
                    break
                
                for activity_data in activities:
                    created = self.save_activity(activity_data)
                    if created:
                        total_new += 1
                    total_synced += 1
                
                if len(activities) < 200:
                    break
                
                page += 1
                time.sleep(0.2)  # Rate limiting
                
            except Exception as e:
                print(f"Error syncing recent activities: {e}")
                break
        
        print(f"Recent sync complete! Total processed: {total_synced}, New activities: {total_new}")
        return total_synced, total_new