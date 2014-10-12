# STANDARD LIB
from functools import wraps

# LIBRARIES
from django.conf import settings
from django.shortcuts import redirect


def registration_must_be_open(func):
    """ A view decorator which ensures that registration must be active. """

    @wraps(func)
    def replacement(*args, **kwargs):
        if not getattr(settings, 'REGISTRATION_OPEN', True):
            return redirect(getattr(settings, 'REGISTRATION_DISALLOWED_URL', 'registration_disallowed'))
        return func(*args, **kwargs)

    return replacement
