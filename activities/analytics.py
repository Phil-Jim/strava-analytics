import pandas as pd
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from .models import Activity


class StravaAnalytics:
    """Analytics service for Strava activity data"""
    
    def __init__(self, user=None):
        if user and user.is_authenticated:
            self.activities = Activity.objects.filter(user=user)
        else:
            self.activities = Activity.objects.none()
    
    def get_activities_dataframe(self, activity_type=None, start_date=None, end_date=None):
        """Convert activities to pandas DataFrame for analysis"""
        queryset = self.activities
        
        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)
        
        if start_date:
            queryset = queryset.filter(start_date__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(start_date__lte=end_date)
        
        # Convert to list of dictionaries
        activities_data = list(queryset.values(
            'id', 'name', 'activity_type', 'start_date', 'distance',
            'moving_time', 'elapsed_time', 'average_speed', 'max_speed',
            'total_elevation_gain', 'average_heartrate', 'max_heartrate',
            'calories'
        ))
        
        if not activities_data:
            return pd.DataFrame()
        
        df = pd.DataFrame(activities_data)
        
        # Convert distance to km and speed to km/h
        df['distance_km'] = df['distance'] / 1000
        df['distance_miles'] = df['distance'] / 1609.34
        df['average_speed_kmh'] = df['average_speed'].fillna(0) * 3.6
        df['average_speed_mph'] = df['average_speed'].fillna(0) * 2.237
        df['max_speed_kmh'] = df['max_speed'].fillna(0) * 3.6
        df['moving_time_hours'] = df['moving_time'] / 3600
        
        # Calculate pace (minutes per km)
        df['pace_min_per_km'] = (df['moving_time'] / 60) / df['distance_km']
        
        # Add date fields for grouping
        df['date'] = pd.to_datetime(df['start_date']).dt.date
        df['year'] = pd.to_datetime(df['start_date']).dt.year
        df['month'] = pd.to_datetime(df['start_date']).dt.month
        df['week'] = pd.to_datetime(df['start_date']).dt.isocalendar().week
        df['day_of_week'] = pd.to_datetime(df['start_date']).dt.day_name()
        
        return df
    
    def get_summary_stats(self, period='all', activity_type=None):
        """Get summary statistics for activities"""
        queryset = self.activities
        
        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)
        
        # Apply date filtering based on period
        now = timezone.now()
        if period == 'week':
            start_date = now - timedelta(days=7)
            queryset = queryset.filter(start_date__gte=start_date)
        elif period == 'month':
            start_date = now - timedelta(days=30)
            queryset = queryset.filter(start_date__gte=start_date)
        elif period == 'year':
            start_date = now - timedelta(days=365)
            queryset = queryset.filter(start_date__gte=start_date)
        
        stats = queryset.aggregate(
            total_activities=Count('id'),
            total_distance=Sum('distance'),
            total_time=Sum('moving_time'),
            total_elevation=Sum('total_elevation_gain'),
            total_calories=Sum('calories'),
            avg_distance=Avg('distance'),
            avg_speed=Avg('average_speed'),
            avg_heartrate=Avg('average_heartrate')
        )
        
        # Convert to more readable units
        stats['total_distance_km'] = (stats['total_distance'] or 0) / 1000
        stats['total_distance_miles'] = (stats['total_distance'] or 0) / 1609.34
        stats['total_time_hours'] = (stats['total_time'] or 0) / 3600
        stats['avg_distance_km'] = (stats['avg_distance'] or 0) / 1000
        stats['avg_speed_kmh'] = (stats['avg_speed'] or 0) * 3.6
        stats['avg_speed_mph'] = (stats['avg_speed'] or 0) * 2.237
        
        return stats
    
    def get_activity_type_breakdown(self, period='all'):
        """Get breakdown of activities by type"""
        queryset = self.activities
        
        # Apply date filtering
        now = timezone.now()
        if period == 'week':
            start_date = now - timedelta(days=7)
            queryset = queryset.filter(start_date__gte=start_date)
        elif period == 'month':
            start_date = now - timedelta(days=30)
            queryset = queryset.filter(start_date__gte=start_date)
        elif period == 'year':
            start_date = now - timedelta(days=365)
            queryset = queryset.filter(start_date__gte=start_date)
        
        breakdown = queryset.values('activity_type').annotate(
            count=Count('id'),
            total_distance=Sum('distance'),
            total_time=Sum('moving_time'),
            avg_distance=Avg('distance'),
            avg_speed=Avg('average_speed')
        ).order_by('-count')
        
        # Convert to readable units
        for item in breakdown:
            item['total_distance_km'] = (item['total_distance'] or 0) / 1000
            item['total_distance_miles'] = (item['total_distance'] or 0) / 1609.34
            item['total_time_hours'] = (item['total_time'] or 0) / 3600
            item['avg_distance_km'] = (item['avg_distance'] or 0) / 1000
            item['avg_distance_miles'] = (item['avg_distance'] or 0) / 1609.34
            item['avg_speed_kmh'] = (item['avg_speed'] or 0) * 3.6
            item['avg_speed_mph'] = (item['avg_speed'] or 0) * 2.237
        
        return list(breakdown)
    
    def get_monthly_trends(self, activity_type=None):
        """Get monthly activity trends"""
        queryset = self.activities
        
        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)
        
        # Get all activities (full history)
        df = self.get_activities_dataframe(activity_type=activity_type)
        if df.empty:
            return []
        
        # Group by year-month
        df['year_month'] = pd.to_datetime(df['start_date']).dt.to_period('M')
        
        monthly_stats = df.groupby('year_month').agg({
            'id': 'count',
            'distance_km': 'sum',
            'distance_miles': 'sum',
            'moving_time_hours': 'sum',
            'average_speed_kmh': 'mean',
            'average_speed_mph': 'mean',
            'calories': 'sum'
        }).reset_index()
        
        monthly_stats.columns = ['month', 'activities', 'distance_km', 'distance_miles', 'time_hours', 'avg_speed_kmh', 'avg_speed_mph', 'calories']
        monthly_stats['month'] = monthly_stats['month'].astype(str)
        
        return monthly_stats.to_dict('records')
    
    def get_weekly_trends(self, weeks=12, activity_type=None):
        """Get weekly activity trends"""
        queryset = self.activities
        
        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)
        
        # Get activities from last N weeks
        weeks_ago = timezone.now() - timedelta(weeks=weeks)
        start_date = weeks_ago
        
        df = self.get_activities_dataframe(activity_type=activity_type, start_date=start_date)
        if df.empty:
            return []
        
        # Group by year-week
        df['year_week'] = pd.to_datetime(df['start_date']).dt.to_period('W')
        
        weekly_stats = df.groupby('year_week').agg({
            'id': 'count',
            'distance_km': 'sum',
            'distance_miles': 'sum',
            'moving_time_hours': 'sum',
            'calories': 'sum'
        }).reset_index()
        
        weekly_stats.columns = ['week', 'activities', 'distance_km', 'distance_miles', 'time_hours', 'calories']
        weekly_stats['week'] = weekly_stats['week'].astype(str)
        
        return weekly_stats.to_dict('records')
    
    def get_personal_records(self, activity_type=None):
        """Get personal records (longest distance, fastest pace, etc.)"""
        queryset = self.activities
        
        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)
        
        if not queryset.exists():
            return {}
        
        records = {}
        
        # Longest distance
        longest = queryset.order_by('-distance').first()
        if longest:
            records['longest_distance'] = {
                'activity': longest,
                'distance_km': longest.distance_km,
                'date': longest.start_date.date()
            }
        
        # Longest time
        longest_time = queryset.order_by('-moving_time').first()
        if longest_time:
            records['longest_time'] = {
                'activity': longest_time,
                'time': longest_time.moving_time_formatted,
                'date': longest_time.start_date.date()
            }
        
        # Fastest speed
        fastest = queryset.filter(average_speed__isnull=False).order_by('-average_speed').first()
        if fastest:
            records['fastest_speed'] = {
                'activity': fastest,
                'speed_kmh': fastest.average_speed_kmh,
                'date': fastest.start_date.date()
            }
        
        # Most elevation
        most_elevation = queryset.filter(
            total_elevation_gain__isnull=False
        ).order_by('-total_elevation_gain').first()
        if most_elevation:
            records['most_elevation'] = {
                'activity': most_elevation,
                'elevation_m': most_elevation.total_elevation_gain,
                'date': most_elevation.start_date.date()
            }
        
        return records
    
    def get_day_of_week_stats(self, activity_type=None):
        """Get activity statistics by day of week"""
        df = self.get_activities_dataframe(activity_type=activity_type)
        
        if df.empty:
            return []
        
        day_stats = df.groupby('day_of_week').agg({
            'id': 'count',
            'distance_km': 'mean',
            'distance_miles': 'mean',
            'moving_time_hours': 'mean',
            'average_speed_kmh': 'mean',
            'average_speed_mph': 'mean'
        }).reset_index()
        
        day_stats.columns = ['day', 'avg_activities', 'avg_distance_km', 'avg_distance_miles', 'avg_time_hours', 'avg_speed_kmh', 'avg_speed_mph']
        
        # Reorder days of week
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_stats['day'] = pd.Categorical(day_stats['day'], categories=day_order, ordered=True)
        day_stats = day_stats.sort_values('day')
        
        return day_stats.to_dict('records')