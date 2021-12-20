from django.db import IntegrityError
from django.test import TestCase

from ..models import Comment, Follow, Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='bond')
        cls.user_1 = User.objects.create_user(username='user_1')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа' * 5,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='hello' * 5
        )
        cls.follow = Follow.objects.create(
            user=cls.user_1,
            author=cls.user
        )

    def test_models_have_correct_object_names(self):
        """We check that __str__ works correctly for models."""
        object_names = {
            self.post: self.post.text[:15],
            self.group: self.group.title,
            self.comment: self.comment.text[:15],
            self.follow: f'{self.follow.user} subscribed to '
                         f'{self.follow.author}'
        }
        for model, expected_value in object_names.items():
            with self.subTest(model=model):
                self.assertEqual(str(model), expected_value)

    def test_verbose_name(self):
        """The verbose_name in the fields is the same as expected."""
        post = self.__class__.post
        field_verboses = {
            'text': 'article',
            'pub_date': 'year of writing',
            'group': 'group name',
            'author': 'author',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_help_text(self):
        """The help_text in the fields is the same as expected."""
        post = self.__class__.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)

    def test_follow_unique_not_following_myself(self):
        """You cannot subscribe to yourself and
        twice to the same author"""
        count_check = Follow.objects.all().count()
        alex = User.objects.create_user(username='alex')
        mike = User.objects.create_user(username='mike')
        Follow.objects.create(
            user=alex,
            author=mike
        )
        self.assertEqual(Follow.objects.all().count(), count_check + 1)
        with self.assertRaises(IntegrityError):
            Follow.objects.create(
                user=alex,
                author=alex)
            Follow.objects.create(
                user=alex,
                author=mike)
