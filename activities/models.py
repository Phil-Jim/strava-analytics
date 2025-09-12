from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class StravaProfile(models.Model):
    """Store user-specific Strava API credentials"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='strava_profile')
    strava_user_id = models.BigIntegerField(unique=True)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    expires_at = models.DateTimeField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - Strava Profile"


class Activity(models.Model):
    ACTIVITY_TYPES = [
        ('Run', 'Run'),
        ('Ride', 'Ride'),
        ('EBikeRide', 'EBikeRide'),
        ('Swim', 'Swim'),
        ('Walk', 'Walk'),
        ('Hike', 'Hike'),
        ('Workout', 'Workout'),
        ('Other', 'Other'),
    ]
    
    # Link to user
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    
    # Strava activity ID (unique per user)
    strava_id = models.BigIntegerField()
    
    # Basic activity information
    name = models.CharField(max_length=200)
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES, default='Other')
    start_date = models.DateTimeField()
    
    # Distance and time
    distance = models.FloatField(help_text="Distance in meters")
    moving_time = models.IntegerField(help_text="Moving time in seconds")
    elapsed_time = models.IntegerField(help_text="Total elapsed time in seconds")
    
    # Speed and pace
    average_speed = models.FloatField(null=True, blank=True, help_text="Average speed in m/s")
    max_speed = models.FloatField(null=True, blank=True, help_text="Max speed in m/s")
    
    # Elevation
    total_elevation_gain = models.FloatField(null=True, blank=True, help_text="Elevation gain in meters")
    
    # Heart rate (if available)
    average_heartrate = models.FloatField(null=True, blank=True)
    max_heartrate = models.FloatField(null=True, blank=True)
    
    # Power (for cycling activities)
    average_watts = models.FloatField(null=True, blank=True)
    max_watts = models.FloatField(null=True, blank=True)
    
    # Calories
    calories = models.IntegerField(null=True, blank=True)
    
    # Location data
    start_latitude = models.FloatField(null=True, blank=True)
    start_longitude = models.FloatField(null=True, blank=True)
    end_latitude = models.FloatField(null=True, blank=True)
    end_longitude = models.FloatField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        unique_together = ['user', 'strava_id']
        indexes = [
            models.Index(fields=['start_date']),
            models.Index(fields=['activity_type']),
            models.Index(fields=['user', 'strava_id']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.activity_type} on {self.start_date.date()}"
    
    @property
    def distance_km(self):
        """Return distance in kilometers"""
        return self.distance / 1000 if self.distance else 0
    
    @property
    def distance_miles(self):
        """Return distance in miles"""
        return self.distance / 1609.34 if self.distance else 0
    
    @property
    def moving_time_formatted(self):
        """Return moving time in HH:MM:SS format"""
        hours = self.moving_time // 3600
        minutes = (self.moving_time % 3600) // 60
        seconds = self.moving_time % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    @property
    def average_pace_per_km(self):
        """Return average pace in minutes per kilometer"""
        if self.distance and self.moving_time:
            distance_km = self.distance / 1000
            pace_seconds = self.moving_time / distance_km
            minutes = int(pace_seconds // 60)
            seconds = int(pace_seconds % 60)
            return f"{minutes:02d}:{seconds:02d}"
        return "N/A"
    
    @property
    def average_speed_kmh(self):
        """Return average speed in km/h"""
        return self.average_speed * 3.6 if self.average_speed else 0
    
    @property
    def average_speed_mph(self):
        """Return average speed in mph"""
        return self.average_speed * 2.237 if self.average_speed else 0


class ActivitySummary(models.Model):
    """Summary statistics for different time periods"""
    
    PERIOD_CHOICES = [
        ('day', 'Day'),
        ('week', 'Week'),
        ('month', 'Month'),
        ('year', 'Year'),
    ]
    
    period_type = models.CharField(max_length=10, choices=PERIOD_CHOICES)
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Activity counts by type
    total_activities = models.IntegerField(default=0)
    run_count = models.IntegerField(default=0)
    ride_count = models.IntegerField(default=0)
    swim_count = models.IntegerField(default=0)
    other_count = models.IntegerField(default=0)
    
    # Distance totals (in meters)
    total_distance = models.FloatField(default=0)
    run_distance = models.FloatField(default=0)
    ride_distance = models.FloatField(default=0)
    swim_distance = models.FloatField(default=0)
    
    # Time totals (in seconds)
    total_moving_time = models.IntegerField(default=0)
    total_elapsed_time = models.IntegerField(default=0)
    
    # Elevation
    total_elevation_gain = models.FloatField(default=0)
    
    # Calories
    total_calories = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['period_type', 'period_start', 'period_end']
        ordering = ['-period_start']
    
    def __str__(self):
        return f"{self.period_type} summary: {self.period_start} to {self.period_end}"
