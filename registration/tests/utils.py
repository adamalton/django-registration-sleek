from functools import wraps
import os

from django.contrib.sites.models import Site


TESTS_TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'templates'),
)


class UninstallSites(object):
    """ A decorator/context manager that makes django.contrib.sites not installed.
        Dirty.
    """

    def __call__(self, original):
        if isinstance(original, type):
            raise TypeError("%s cannot be used as a class decorator" % self.__class__.__name__)

        @wraps(original)
        def replacement(*args, **kwargs):
            with self:
                return original(*args, **kwargs)

        return replacement

    def __enter__(self):
        configs = Site._meta.apps.app_configs
        app_label = Site._meta.app_label
        self.original_app_config = configs.get(app_label)
        if self.original_app_config:
            del configs[app_label]

    def __exit__(self, *args):
        if self.original_app_config:
            Site._meta.apps.app_configs[Site._meta.app_label] = self.original_app_config
