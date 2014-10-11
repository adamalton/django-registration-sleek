"""
Views which allow users to create and activate accounts.

"""

from django.shortcuts import redirect
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from registration import signals
from registration.forms import RegistrationForm


class RegistrationView(FormView):
    """
    Base class for user registration views.

    """
    disallowed_url = 'registration_disallowed'
    form_class = RegistrationForm
    http_method_names = ['get', 'post', 'head', 'options', 'trace']
    success_url = None
    template_name = 'registration/registration_form.html'

    def dispatch(self, request, *args, **kwargs):
        """
        Check that user signup is allowed before even bothering to
        dispatch or do other processing.

        """
        if not self.registration_allowed(request):
            return redirect(self.disallowed_url)
        return super(RegistrationView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, request, form):
        new_user = self.register(request, **form.cleaned_data)
        success_url = self.get_success_url()

        # success_url may be a simple string, or a tuple providing the
        # full argument set for redirect(). Attempting to unpack it
        # tells us which one it is.
        try:
            to, args, kwargs = success_url
            return redirect(to, *args, **kwargs)
        except ValueError:
            return redirect(success_url)

    def registration_allowed(self, request):
        """
        Override this to enable/disable user registration, either
        globally or on a per-request basis.

        """
        return True

    def register(self, request, **cleaned_data):
        """
        Implement user-registration logic here. Access to both the
        request and the full cleaned_data of the registration form is
        available here.

        """
        raise NotImplementedError


class ActivationView(TemplateView):
    """
    Base class for user activation views.

    """
    http_method_names = ['get']
    template_name = 'registration/activate.html'

    def get(self, request, *args, **kwargs):
        activated_user = self.activate(request, *args, **kwargs)
        if activated_user:
            signals.user_activated.send(sender=self.__class__,
                                        user=activated_user,
                                        request=request)
            success_url = self.get_success_url()
            try:
                to, args, kwargs = success_url
                return redirect(to, *args, **kwargs)
            except ValueError:
                return redirect(success_url)
        return super(ActivationView, self).get(request, *args, **kwargs)

    def activate(self, request, *args, **kwargs):
        """
        Implement account-activation logic here.

        """
        raise NotImplementedError

    def get_success_url(self):
        raise NotImplementedError
