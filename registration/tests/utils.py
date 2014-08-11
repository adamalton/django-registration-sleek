import os

from django.contrib.sites.models import Site


TESTS_TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'templates'),
)

