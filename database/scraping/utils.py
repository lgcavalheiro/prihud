'''
Module that provides utilities for the scraping module.
'''

import json
import os
from threading import Thread
from datetime import datetime
from django.core.management import call_command
from prihud.settings import EXPLORATION_RESULTS_DIR


running_commands = []


class ScrapeStarter(Thread):
    ''' Class that wraps scrape call command so it can be executed in a separate thread '''

    frequency = None
    targets = []

    def __init__(self, frequency, targets):
        super().__init__()
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


def run_explore_command(url, selector_type, selector):
    ''' Function for running the explore command and saving the exploration results '''

    result = call_command('explore', u=url, t=selector_type, s=selector)
    exploration_result = json.loads(result)

    file_url = url.replace('https://', '').replace('/', '').replace(' ', '_')
    now = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    result_file = os.path.join(
        EXPLORATION_RESULTS_DIR, f'explore_{file_url}_{now}.html')
    exploration_result['result_file'] = result_file

    with open(result_file, 'w', encoding='utf-8') as file:
        file.write(exploration_result['page_source'])

    return exploration_result
