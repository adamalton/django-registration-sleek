# Django registraion sleek

This is an updated version of the popular django-registration library, now compatible with Django 1.7.

Note that if you're using a custom user model then you'll need to also write your own custom registration backend.


USAGE:

At the moment this is pretty similar to the original Django Regisration app, but you can now use it with a custom user model.  The main thing that you need to do in order to make this work is to define a custom form class for registration.  This should implement something similar to `registration.forms.RegistrationForm`, but using whatever fields your user model has.

TODO:

* Add a `REGISTRATION_FORM = 'myapp.forms.RegistrationForm'` setting so that you can specify a form which works with your own custom user model without you having to write your own custom backend.
* Re-build/destroy the backends stuff, and maybe the class-based views as well.  I hate it all.
* Put this on pypi.

Old docs are available at [https://django-registration.readthedocs.org/](https://django-registration.readthedocs.org/).  Updated docs are available in this repo under docs/._
