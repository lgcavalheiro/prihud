import json
from django.core.management.base import BaseCommand
from database.scraping.impl.exploration_job import ExplorationJob
from database.models import Target


class Command(BaseCommand):
    help = 'Explore page from within Prihud'

    def add_arguments(self, parser):
        parser.add_argument('-u', type=str, dest='url', help='Target url')

        parser.add_argument(
            '-t', type=str, dest='selector_type', help="Selector type")

        parser.add_argument('-s', type=str, dest='selector',
                            help="Selector to be used")

    def handle(self, *args, **options):
        url, selector_type, selector = options['url'], options['selector_type'], options['selector']

        target = Target(
            url=url, custom_selector_type=selector_type, custom_selector=selector)

        result = ExplorationJob(target).start()

        return json.dumps(result, indent=2)
