import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Follow, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsVIEWSTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.tom = User.objects.create_user(username='Tom')
        cls.user = User.objects.create_user(username='userman')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='something_slug',
            description='Тестовое описание',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        for i in range(15):
            if i != 0:
                cls.post = Post.objects.create(
                    author=cls.user,
                    text='Текст о' + str(i),
                    group=cls.group,
                    image=cls.uploaded
                )
            else:
                cls.post = Post.objects.create(
                    author=cls.user,
                    text='Тестовая группа' + str(i),
                    image=cls.uploaded
                )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.__class__.user)

    def test_pages_uses_correct_namespase_name(self):
        """The template uses the correct namespase:name."""
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}):
                'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}):
                'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_paginator_pages_contains_correct_context(self):
        """Check the paginator and correctly weld the context."""
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user}):
                'posts/profile.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']),
                                 settings.PAGINATOR_COUNT)
                first_object = response.context['page_obj'][0]
                post_text_0 = first_object.text
                post_author_0 = first_object.author.username
                post_group_0 = first_object.group.title
                self.assertEqual(post_text_0, self.post.text)
                self.assertEqual(post_author_0, self.post.author.username)
                self.assertEqual(post_group_0, self.post.group.title)
            with self.subTest(template=template + '?page=2'):
                response = self.authorized_client.get(reverse_name + '?page=2')
                if template == 'posts/group_list.html':
                    self.assertEqual(len(response.context['page_obj']), 4)
                else:
                    self.assertEqual(len(response.context['page_obj']), 5)

    def test_create_edit_pages_show_correct_context(self):
        """Check form fields."""
        templates_page_names = {
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}):
                'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                form_fields = {
                    'text': forms.fields.CharField,
                    'group': forms.models.ModelChoiceField,
                    'image': forms.fields.ImageField,
                }
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    response = self.authorized_client.get(reverse_name)
                    form_field = response.context['form'].fields[value]
                    self.assertIsInstance(form_field, expected)

    def test_post_detail_edit_pages_show_correct_context(self):
        """The post_detail and post_edit templates
        are well-formed with the correct context."""
        templates_page_names = {
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}):
                'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}):
                'posts/create_post.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(response.context['post'].
                                 author.username, self.post.author.username)
                self.assertEqual(response.context['post'].
                                 text, self.post.text)
                self.assertEqual(response.context['post'].group,
                                 self.post.group)

    def test_image_context_exists(self):
        """Checking that when displaying a post with a picture,
        the image is transmitted in the context."""
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}):
                'posts/post_detail.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user}):
                'posts/profile.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                if template == 'posts/post_detail.html':
                    self.assertTrue(response.context['post'].image)
                else:
                    self.assertTrue(response.context['page_obj'][0].image)

    def test_cache_index(self):
        """Check cache in index."""
        response = self.authorized_client.get(reverse('posts:index'))
        control_text = Post.objects.get(pk=self.post.pk).text
        self.assertIn(control_text, response.content.decode('utf-8'))
        Post.objects.get(pk=self.post.pk).delete()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertIn(control_text, response.content.decode('utf-8'))
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertNotIn(control_text, response.content.decode('utf-8'))

    def test_follow_add_delete(self):
        """An authorized user can subscribe to other
        users and remove them from subscriptions."""
        count_check = Follow.objects.all().count()
        self.guest_client.get(reverse('posts:profile_follow',
                                      kwargs={'username': self.tom}))
        self.assertEqual(Follow.objects.all().count(), count_check)
        self.authorized_client.get(reverse('posts:profile_follow',
                                           kwargs={'username': self.tom}))
        self.assertEqual(Follow.objects.all().count(), count_check + 1)
        self.guest_client.get(reverse('posts:profile_unfollow',
                                      kwargs={'username': self.tom}))
        self.assertEqual(Follow.objects.all().count(), count_check + 1)
        self.authorized_client.get(reverse('posts:profile_unfollow',
                                           kwargs={'username': self.tom}))
        self.assertEqual(Follow.objects.all().count(), count_check)

    def test_new_entry_show_line(self):
        """Adding a new entry to the feed to the subscribed user."""
        Follow.objects.create(
            user=self.tom,
            author=self.user
        )
        text = 'hay Mr. Anderson'
        Post.objects.create(
            author=self.user,
            text='hay Mr. Anderson',
            group=self.group,
        )
        self.authorized_client.force_login(self.user)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertNotIn(text, response.content.decode('utf-8'))
        self.authorized_client.force_login(self.tom)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertIn(text, response.content.decode('utf-8'))
