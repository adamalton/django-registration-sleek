from django.contrib.auth.models import User
from django.contrib.auth.tests.utils import skipIfCustomUser
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.utils import override_settings

from registration.forms import RegistrationForm
from registration.tests.utils import TESTS_TEMPLATE_DIRS


@override_settings(TEMPLATE_DIRS=TESTS_TEMPLATE_DIRS)
class SimpleBackendViewTests(TestCase):
    urls = 'registration.backends.simple.urls'

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
        Registration creates a new account and logs the user in.

        """
        resp = self.client.post(reverse('registration_register'),
                                data={'username': 'bob',
                                      'email': 'bob@example.com',
                                      'password1': 'secret',
                                      'password2': 'secret'})

        new_user = User.objects.get(username='bob')
        self.assertEqual(302, resp.status_code)
        self.failUnless(reverse('registration_complete') in resp['Location'])

        self.failUnless(new_user.check_password('secret'))
        self.assertEqual(new_user.email, 'bob@example.com')

        # New user must be active.
        self.failUnless(new_user.is_active)

        # New user must be logged in.
        resp = self.client.get(reverse('registration_register'))
        self.failUnless(resp.context['user'].is_authenticated())

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
