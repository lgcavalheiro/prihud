from django.core.management.base import BaseCommand
from prihud.logger import AppriseLogger
from datetime import datetime


class Command(BaseCommand):
    help = 'Pings the remote logging solution, use for testing cronjobs'

    def handle(self, *args, **options):
        logger = AppriseLogger()
        logger.success(
            f'Pinging at {datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}')
        logger = None
