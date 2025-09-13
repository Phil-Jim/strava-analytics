from django.urls import path
from . import views, auth_views

urlpatterns = [
    # Authentication
    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout_view, name='logout'),
    path('register/', auth_views.register_view, name='register'),
    path('auth/strava/', auth_views.strava_auth, name='strava_auth'),
    path('auth/strava/callback/', auth_views.strava_callback, name='strava_callback'),
    path('sync/', auth_views.sync_activities_view, name='sync_activities'),
    
    # Health check
    path('health/', views.health_check, name='health_check'),
    path('debug/', views.debug_env, name='debug_env'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # API endpoints
    path('api/stats/', views.api_stats, name='api_stats'),
    path('api/breakdown/', views.api_activity_breakdown, name='api_breakdown'),
    path('api/monthly-trends/', views.api_monthly_trends, name='api_monthly_trends'),
    path('api/weekly-trends/', views.api_weekly_trends, name='api_weekly_trends'),
    path('api/personal-records/', views.api_personal_records, name='api_personal_records'),
    path('api/day-of-week/', views.api_day_of_week_stats, name='api_day_of_week'),
    path('api/activities/', views.api_activities, name='api_activities'),
    
    # Legal pages
    path('privacy/', views.privacy_policy, name='privacy_policy'),
    path('data-deletion/', views.data_deletion, name='data_deletion'),
]