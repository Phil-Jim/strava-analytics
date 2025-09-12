from django.core.management.base import BaseCommand
from activities.strava_service import StravaService


class Command(BaseCommand):
    help = 'Sync activities from Strava API'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit number of activities to sync',
        )
        parser.add_argument(
            '--recent',
            type=int,
            help='Sync activities from last N days only',
        )
    
    def handle(self, *args, **options):
        strava_service = StravaService()
        
        try:
            # Test API connection first
            athlete = strava_service.get_athlete_info()
            self.stdout.write(
                self.style.SUCCESS(f'Connected to Strava as: {athlete["firstname"]} {athlete["lastname"]}')
            )
            
            if options['recent']:
                # Sync recent activities only
                total, new = strava_service.sync_recent_activities(days=options['recent'])
            else:
                # Sync all activities
                total, new = strava_service.sync_all_activities(limit=options['limit'])
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully synced {total} activities ({new} new)'
                )
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error syncing activities: {str(e)}')
            )