from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Dummy collectstatic command that does nothing'

    def add_arguments(self, parser):
        parser.add_argument('--noinput', action='store_true', help='Do not prompt for input')
        parser.add_argument('--clear', action='store_true', help='Clear existing files')

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Static files collection skipped - using inline CSS')
        )