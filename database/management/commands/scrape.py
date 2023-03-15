import os
from django.core.management.base import BaseCommand
from database.scraping.impl.scraping_job import ScrapingJob
from database.models import Frequencies, Target


class Command(BaseCommand):
    help = 'Run scraper for fetching price data'

    def add_arguments(self, parser):
        parser.add_argument('-f', type=str, dest='frequency',
                            help='Defines the target frequency to scrape')

        parser.add_argument('-i', type=int, dest='ids', action="append",
                            help="Defines only some targets to be scraped by their id")

    def handle(self, *args, **options):
        if (options['ids']):
            targets = Target.objects.filter(pk__in=options['ids']).all()
        else:
            targets = Target.objects.filter(
                frequency=options["frequency"]).all()

        if len(targets) == 0:
            self.stderr.write("Found no targets for this scraping job")
            return

        report = ScrapingJob(targets).start()
        os.system("killall -9 geckodriver")
        os.system("killall -9 firefox-esr")

        self.stdout.write("=== Report results ===")
        self.stdout.write(f"Started at: {report['start_time']}")
        self.stdout.write(f"End at: {report['end_time']}")
        self.stdout.write(f"Duration: {report['duration']}")
        self.stdout.write(f"Results: {report['result']} successes")

        if len(report['failures']) > 0:
            self.stderr.write(
                f"=== Had {len(report['failures'])} failures ===")
            for failure in report['failures']:
                self.stderr.write(
                    f'{failure[0].alias or failure[0].url}: {failure[1]}')
