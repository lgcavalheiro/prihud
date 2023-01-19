from prihud.logger import AppriseLogger


class TestLogger(AppriseLogger):
    __apr = None

    def __init__(self):
        pass

    def __del__(self):
        pass

    def info(self, body, title=None):
        print(body, title, "INFO")

    def fail(self, body, title=None):
        print(body, title, "FAILURE")

    def success(self, body, title=None):
        print(body, title, "SUCCESS")

    def warn(self, body, title=None):
        print(body, title, "WARNING")
