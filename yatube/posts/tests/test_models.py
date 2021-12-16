from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='bond')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
        )

    def test_models_have_correct_object_names(self):
        """We check that __str__ works correctly for models."""
        post = self.__class__.post
        expected_text = post.text
        self.assertEqual(expected_text[:15], str(post))
        group = self.__class__.group
        expected_title = group.title
        self.assertEqual(expected_title, str(group))

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
