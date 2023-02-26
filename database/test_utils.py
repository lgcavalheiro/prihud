'''
Module providing test utilities for the database app.
'''

from prihud.logger import AppriseLogger


class TestLogger(AppriseLogger):
    ''' Class that is used to log messages 
    during tests in place of the standard logger class '''

    def info(self, body, title=None):
        print(body, title, "INFO")

    def fail(self, body, title=None):
        print(body, title, "FAILURE")

    def success(self, body, title=None):
        print(body, title, "SUCCESS")

    def warn(self, body, title=None):
        print(body, title, "WARNING")
