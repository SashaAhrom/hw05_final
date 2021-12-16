import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='userman')
        cls.group = Group.objects.create(
            pk=1,
            title='Тестовая группа',
            slug='something_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
        )
        cls.comments = Comment.objects.create(
            author=cls.user,
            post=cls.post,
            text='new comment')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.__class__.user)

    def test_create_post(self):
        """Check a new record is created in Post."""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'author': self.user,
            'text': 'Новый тестовый текст ',
            'group': self.group.pk,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile',
                                               kwargs={'username': self.user}))
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post(self):
        """Сhecking the editing of a record in Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Редактированный тестовый текст',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             reverse('posts:post_detail',
                                     kwargs={'post_id': self.post.pk}))
        self.assertEqual(Post.objects.count(), posts_count)
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}))
        self.assertEqual(response.context['post'].text,
                         'Редактированный тестовый текст')

    def test_comment_only_authorized_user_add_comment(self):
        """Only an authorized user can add comments."""
        post = Post.objects.get(pk=self.post.pk)
        comment_count = post.comments.count()
        url = reverse('posts:add_comment',
                      kwargs={'post_id': self.post.pk})
        form_data = {
            'post': post.pk,
            'author': self.post.author,
            'text': 'all be back',
        }
        self.guest_client.post(url,
                               data=form_data,
                               follow=True)
        self.assertEqual(post.comments.count(), comment_count)
        response_auth = self.authorized_client.post(url,
                                                    data=form_data,
                                                    follow=True)
        self.assertEqual(post.comments.count(), comment_count + 1)
        self.assertTrue(response_auth.context['comments'].get(
            text='all be back'))
