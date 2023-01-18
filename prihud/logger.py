import apprise
from prihud.settings import DISCORD_HOOK


class AppriseLogger():
    __apr = None

    def __init__(self):
        if not DISCORD_HOOK:
            raise Exception("No discord webhook provided")

        if not self.__apr:
            self.__apr = apprise.Apprise()

        self.__apr.add(DISCORD_HOOK)

    def __del__(self):
        self.__apr.clear()
        self.__apr = None

    def info(self, body, title=None):
        self.__apr.notify(body, title, notify_type=apprise.NotifyType.INFO)

    def fail(self, body, title=None):
        self.__apr.notify(body, title, notify_type=apprise.NotifyType.FAILURE)

    def success(self, body, title=None):
        self.__apr.notify(body, title, notify_type=apprise.NotifyType.SUCCESS)

    def warn(self, body, title=None):
        self.__apr.notify(body, title, notify_type=apprise.NotifyType.WARNING)
