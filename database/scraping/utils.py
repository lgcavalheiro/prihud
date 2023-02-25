from django.core.management import call_command
from threading import Thread
from datetime import datetime


running_commands = []


class ScrapeStarter(Thread):
    frequency = None
    targets = []

    def __init__(self, frequency, targets):
        super(ScrapeStarter, self).__init__()
        self.frequency = frequency
        self.targets = targets
        self.name = f'scrape_{datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}'
        running_commands.append(self.name)

    def run(self):
        if self.frequency:
            call_command('scrape', f=self.frequency)
        elif len(self.targets) > 0:
            call_command('scrape', i=self.targets)
        running_commands.remove(self.name)
