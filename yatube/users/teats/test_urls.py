import base64
from http import HTTPStatus

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import User

TEMPLATES_NAMESPACE_URLS = [
    ['users/signup.html', reverse('users:signup'), '/auth/signup/'],
    ['users/login.html', reverse('users:login'), '/auth/login/'],
    ['users/password_change_form.html', reverse('users:password_change_form'),
     '/auth/password_change/'],
    ['users/password_change_done.html', reverse('users:password_change_done'),
     '/auth/password_change/done/'],
    ['users/password_reset_form.html', reverse('users:password_reset_form'),
     '/auth/password_reset/'],
    ['users/password_reset_done.html', reverse('users:password_reset_done'),
     '/auth/password_reset/done/'],
    ['users/password_reset_confirm.html', None, None],
    ['users/password_reset_complete.html',
     reverse('users:password_reset_complete'),
     '/auth/reset/done/'],
    ['users/logged_out.html', reverse('users:logout'), '/auth/logout/']
]


class UsersURLTests(TestCase):
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
        url_reset = f'/auth/reset/{self.user_b64}/set-password/'
        self.TEMPLATES_NAMESPACE_URLS[6][2] = url_reset

    def test_url_correct_template_status_code_unauthorized(self):
        """Checking status_code and URL-the address
        uses the appropriate template."""
        for template, name, url in self.TEMPLATES_NAMESPACE_URLS[:2]:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK.value)
                self.assertTemplateUsed(response, template)

    def test_url_correct_template_status_code_authorized(self):
        """Checking status_code and URL-the address
        uses the appropriate template."""
        for template, name, url in self.TEMPLATES_NAMESPACE_URLS[2:]:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK.value)
                self.assertTemplateUsed(response, template)
