import base64

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import User
from .test_urls import TEMPLATES_NAMESPACE_URLS


class UsersViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='userman',
                                            password='fdijsojspH12m',
                                            email='idoaoavnh@gmail.com')

    def setUp(self):
        self.user_b64 = base64.b64encode(f'{self.__class__.user.id}'.encode())
        self.token = PasswordResetTokenGenerator().make_token(
            self.__class__.user)
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.__class__.user)
        self.TEMPLATES_NAMESPACE_URLS = TEMPLATES_NAMESPACE_URLS
        self.TEMPLATES_NAMESPACE_URLS[6][1] = reverse(
            'users:password_reset_confirm',
            kwargs={'uidb64': self.user_b64,
                    'token': 'set-password'})

    def test_pages_uses_correct_namespase_name(self):
        """The template uses the correct namespase:name."""
        for template, reverse_name, url in self.TEMPLATES_NAMESPACE_URLS:
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_exist_form(self):
        """Form submission validation."""
        response = self.guest_client.get(self.TEMPLATES_NAMESPACE_URLS[0][1])
        self.assertIsNotNone(response.context['form'])
