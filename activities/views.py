from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .models import Activity
from .analytics import StravaAnalytics


def health_check(request):
    """Simple health check view for debugging"""
    return HttpResponse("OK - Django is working (v2)", content_type="text/plain")


def debug_env(request):
    """Debug view to check environment variables"""
    import os
    from django.conf import settings
    
    env_vars = {
        'FACEBOOK_CLIENT_ID': os.getenv('FACEBOOK_CLIENT_ID', 'Not set'),
        'FACEBOOK_CLIENT_SECRET': 'Set' if os.getenv('FACEBOOK_CLIENT_SECRET') else 'Not set',
        'STRAVA_CLIENT_ID': os.getenv('STRAVA_CLIENT_ID', 'Not set'),
        'STRAVA_CLIENT_SECRET': 'Set' if os.getenv('STRAVA_CLIENT_SECRET') else 'Not set',
        'DEBUG': settings.DEBUG,
        'SOCIALACCOUNT_PROVIDERS_COUNT': len(settings.SOCIALACCOUNT_PROVIDERS),
    }
    
    html = "<h2>Environment Check</h2><ul>"
    for key, value in env_vars.items():
        html += f"<li><strong>{key}:</strong> {value}</li>"
    html += "</ul>"
    
    return HttpResponse(html)


def dashboard(request):
    """Main dashboard view - temporarily remove login requirement for debugging"""
    try:
        if request.user.is_authenticated:
            analytics = StravaAnalytics(user=request.user)
            
            # Get basic stats
            stats = analytics.get_summary_stats()
            activity_breakdown = analytics.get_activity_type_breakdown()
            personal_records = analytics.get_personal_records()
            
            context = {
                'stats': stats,
                'activity_breakdown': activity_breakdown,
                'personal_records': personal_records,
            }
            
            return render(request, 'activities/dashboard.html', context)
        else:
            return HttpResponse("Please log in to view dashboard. <a href='/accounts/login/'>Login</a>")
    
    except Exception as e:
        import traceback
        # For debugging, return detailed error info
        return HttpResponse(f"Dashboard Error: {str(e)}<br><br>Traceback:<br><pre>{traceback.format_exc()}</pre>", status=500)


@require_http_methods(["GET"])
@login_required(login_url='/accounts/login/')
def api_stats(request):
    """API endpoint for summary statistics"""
    period = request.GET.get('period', 'all')
    activity_type = request.GET.get('type', None)
    
    analytics = StravaAnalytics(user=request.user)
    stats = analytics.get_summary_stats(period=period, activity_type=activity_type)
    
    return JsonResponse(stats)


@require_http_methods(["GET"])
@login_required(login_url='/accounts/login/')
def api_activity_breakdown(request):
    """API endpoint for activity type breakdown"""
    period = request.GET.get('period', 'all')
    
    analytics = StravaAnalytics(user=request.user)
    breakdown = analytics.get_activity_type_breakdown(period=period)
    
    return JsonResponse({'breakdown': breakdown})


@require_http_methods(["GET"])
@login_required(login_url='/accounts/login/')
def api_monthly_trends(request):
    """API endpoint for monthly trends"""
    activity_type = request.GET.get('type', None)
    
    analytics = StravaAnalytics(user=request.user)
    trends = analytics.get_monthly_trends(activity_type=activity_type)
    
    return JsonResponse({'trends': trends})


@require_http_methods(["GET"])
@login_required(login_url='/accounts/login/')
def api_weekly_trends(request):
    """API endpoint for weekly trends"""
    weeks = int(request.GET.get('weeks', 12))
    activity_type = request.GET.get('type', None)
    
    analytics = StravaAnalytics(user=request.user)
    trends = analytics.get_weekly_trends(weeks=weeks, activity_type=activity_type)
    
    return JsonResponse({'trends': trends})


@require_http_methods(["GET"])
@login_required(login_url='/accounts/login/')
def api_personal_records(request):
    """API endpoint for personal records"""
    activity_type = request.GET.get('type', None)
    
    analytics = StravaAnalytics(user=request.user)
    records = analytics.get_personal_records(activity_type=activity_type)
    
    return JsonResponse({'records': records})


@require_http_methods(["GET"])
@login_required(login_url='/accounts/login/')
def api_day_of_week_stats(request):
    """API endpoint for day of week statistics"""
    activity_type = request.GET.get('type', None)
    
    analytics = StravaAnalytics(user=request.user)
    stats = analytics.get_day_of_week_stats(activity_type=activity_type)
    
    return JsonResponse({'stats': stats})


@require_http_methods(["GET"])
@login_required(login_url='/accounts/login/')
def api_activities(request):
    """API endpoint for activity list with filtering"""
    activity_type = request.GET.get('type', None)
    limit = int(request.GET.get('limit', 50))
    
    queryset = Activity.objects.filter(user=request.user)
    
    if activity_type:
        queryset = queryset.filter(activity_type=activity_type)
    
    activities = queryset[:limit]
    
    activity_data = []
    for activity in activities:
        activity_data.append({
            'id': activity.id,
            'name': activity.name,
            'type': activity.activity_type,
            'date': activity.start_date.isoformat(),
            'distance_km': activity.distance_km,
            'distance_miles': activity.distance_miles,
            'moving_time': activity.moving_time_formatted,
            'average_speed_kmh': activity.average_speed_kmh,
            'average_speed_mph': activity.average_speed_mph,
            'elevation_gain': activity.total_elevation_gain,
            'calories': activity.calories,
        })
    
    return JsonResponse({'activities': activity_data})


def privacy_policy(request):
    """Privacy policy page for Facebook compliance"""
    return render(request, 'activities/privacy_policy.html')


def data_deletion(request):
    """Data deletion instructions for Facebook compliance"""
    return render(request, 'activities/data_deletion.html')
