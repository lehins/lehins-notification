
VERSION = (1, 0, 0) # following PEP 386

def get_version():
    return "%s.%s.%s" % VERSION

__version__ = get_version()

default_app_config = 'notification.apps.NotificationConfig'
