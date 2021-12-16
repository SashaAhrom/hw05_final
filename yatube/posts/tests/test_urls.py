from http import HTTPStatus

from django.test import Client, TestCase

from ..models import Group, Post, User


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_alex = User.objects.create_user(username='user_alex')
        cls.user = User.objects.create_user(username='userman')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='something_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.__class__.user)

    def test_page_not_exist(self):
        """This page does not exist."""
        response = self.guest_client.get('/strange_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND.value)

    def test_url_correct_template_status_code_unauthorized(self):
        """Checking status_code and URL-the address
        uses the appropriate template."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user}/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK.value)
                self.assertTemplateUsed(response, template)

    def test_url_correct_template_status_code_authorized(self):
        """Checking status_code and URL-the address
        uses the appropriate template."""
        templates_url_names = {
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK.value)
                self.assertTemplateUsed(response, template)

    def test_create_url_redirect_anonymous_to_login(self):
        """The page / create / will redirect the anonymous user
        to the login page."""
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/')

    def test_posts_edit_url_redirect_authorized(self):
        """The page /posts/<post_id>/edit/ will redirect the authorized user
        to /posts/<post_id>/."""
        self.authorized_client = Client()
        self.authorized_client.force_login(self.__class__.user_alex)
        response = self.authorized_client.get(f'/posts/{self.post.pk}/edit/')
        self.assertRedirects(response, f'/posts/{self.post.pk}/')

    def test_comment_only_authorized_user(self):
        """Only an authorized user can add comments."""
        response = self.guest_client.get('/create/', follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK.value)
