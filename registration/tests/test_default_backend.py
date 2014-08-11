import datetime

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tests.utils import skipIfCustomUser
from django.core import mail
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.utils import override_settings

from registration.forms import RegistrationForm
from registration.models import RegistrationProfile
from registration.tests.utils import TESTS_TEMPLATE_DIRS, UninstallSites


@override_settings(TEMPLATE_DIRS=TESTS_TEMPLATE_DIRS)
@override_settings(ACCOUNT_ACTIVATION_DAYS=7)
class DefaultBackendViewTests(TestCase):
    """
    Test the default registration backend.

    Running these tests successfully will require two templates to be
    created for the sending of activation emails; details on these
    templates and their contexts may be found in the documentation for
    the default backend.

    """
    urls = 'registration.backends.default.urls'

    def test_allow(self):
        """
        The setting ``REGISTRATION_OPEN`` appropriately controls
        whether registration is permitted.

        """
        with override_settings(REGISTRATION_OPEN=True):
            resp = self.client.get(reverse('registration_register'))
            self.assertEqual(200, resp.status_code)

        with override_settings(REGISTRATION_OPEN=False):
            # Now all attempts to hit the register view should redirect to
            # the 'registration is closed' message.
            resp = self.client.get(reverse('registration_register'))
            self.assertRedirects(resp, reverse('registration_disallowed'))

            resp = self.client.post(reverse('registration_register'),
                                    data={'username': 'bob',
                                          'email': 'bob@example.com',
                                          'password1': 'secret',
                                          'password2': 'secret'})
            self.assertRedirects(resp, reverse('registration_disallowed'))


    def test_registration_get(self):
        """
        HTTP ``GET`` to the registration view uses the appropriate
        template and populates a registration form into the context.

        """
        resp = self.client.get(reverse('registration_register'))
        self.assertEqual(200, resp.status_code)
        self.assertTemplateUsed(resp,
                                'registration/registration_form.html')
        self.failUnless(isinstance(resp.context['form'],
                        RegistrationForm))

    @skipIfCustomUser
    def test_registration(self):
        """
        Registration creates a new inactive account and a new profile
        with activation key, populates the correct account data and
        sends an activation email.

        """
        resp = self.client.post(reverse('registration_register'),
                                data={'username': 'bob',
                                      'email': 'bob@example.com',
                                      'password1': 'secret',
                                      'password2': 'secret'})
        self.assertRedirects(resp, reverse('registration_complete'))

        new_user = User.objects.get(username='bob')

        self.failUnless(new_user.check_password('secret'))
        self.assertEqual(new_user.email, 'bob@example.com')

        # New user must not be active.
        self.failIf(new_user.is_active)

        # A registration profile was created, and an activation email
        # was sent.
        self.assertEqual(RegistrationProfile.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)

    @UninstallSites()
    @skipIfCustomUser
    def test_registration_no_sites(self):
        """
        Registration still functions properly when
        ``django.contrib.sites`` is not installed; the fallback will
        be a ``RequestSite`` instance.

        """
        # Site._meta.installed = False

        resp = self.client.post(reverse('registration_register'),
                                data={'username': 'bob',
                                      'email': 'bob@example.com',
                                      'password1': 'secret',
                                      'password2': 'secret'})
        self.assertEqual(302, resp.status_code)

        new_user = User.objects.get(username='bob')

        self.failUnless(new_user.check_password('secret'))
        self.assertEqual(new_user.email, 'bob@example.com')

        self.failIf(new_user.is_active)

        self.assertEqual(RegistrationProfile.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)

        # Site._meta.installed = True

    @skipIfCustomUser
    def test_registration_failure(self):
        """
        Registering with invalid data fails.

        """
        resp = self.client.post(reverse('registration_register'),
                                data={'username': 'bob',
                                      'email': 'bob@example.com',
                                      'password1': 'secret',
                                      'password2': 'notsecret'})
        self.assertEqual(200, resp.status_code)
        self.failIf(resp.context['form'].is_valid())
        self.assertEqual(0, len(mail.outbox))

    @skipIfCustomUser
    def test_activation(self):
        """
        Activation of an account functions properly.

        """
        resp = self.client.post(reverse('registration_register'),
                                data={'username': 'bob',
                                      'email': 'bob@example.com',
                                      'password1': 'secret',
                                      'password2': 'secret'})

        profile = RegistrationProfile.objects.get(user__username='bob')

        resp = self.client.get(reverse('registration_activate',
                                       args=(),
                                       kwargs={'activation_key': profile.activation_key}))
        self.assertRedirects(resp, reverse('registration_activation_complete'))

    @skipIfCustomUser
    def test_activation_expired(self):
        """
        An expired account can't be activated.

        """
        resp = self.client.post(reverse('registration_register'),
                                data={'username': 'bob',
                                      'email': 'bob@example.com',
                                      'password1': 'secret',
                                      'password2': 'secret'})

        profile = RegistrationProfile.objects.get(user__username='bob')
        user = profile.user
        user.date_joined -= datetime.timedelta(days=settings.ACCOUNT_ACTIVATION_DAYS)
        user.save()

        resp = self.client.get(reverse('registration_activate',
                                       args=(),
                                       kwargs={'activation_key': profile.activation_key}))

        self.assertEqual(200, resp.status_code)
        self.assertTemplateUsed(resp, 'registration/activate.html')
        self.failIf('activation_key' in resp.context)
