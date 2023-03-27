from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост. Данный текст не отображется в методе str.',
        )
        cls.group_model_specs = [
            {
                'field_name': 'title',
                'verbose_name': 'Название группы',
                'help_text': 'Введите название группы',
            },
            {
                'field_name': 'slug',
                'verbose_name': 'Уникальный идентификатор группы',
                'help_text': (
                    'Введите идентификатор, который будет частью URL '
                    'страницы: допустимо использование латинских букв, символ '
                    'тире и нижнее подчёркивание'
                ),
            },
            {
                'field_name': 'description',
                'verbose_name': 'Описание группы',
                'help_text': (
                    'Добавьте полное описание группы, чтобы вам было проще '
                    'найти единомышленников'
                ),
            },
        ]
        cls.post_model_specs = [
            {
                'field_name': 'text',
                'verbose_name': 'Текст публикации',
                'help_text': 'Текст нового поста',
            },
            {
                'field_name': 'pub_date',
                'verbose_name': 'Дата публикации',
                'help_text': '',
            },
            {
                'field_name': 'author',
                'verbose_name': 'Автор публикации',
                'help_text': 'Выберите автора публикации',
            },
            {
                'field_name': 'group',
                'verbose_name': 'Группа публикации',
                'help_text': 'Группа, к которой будет относиться пост',
            },
        ]

    def test_group_model_have_correct_object_names(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        group = PostModelTest.group
        expected_group_name = group.title
        self.assertEqual(expected_group_name, str(group))

    def test_group_verbose_names(self):
        """verbose_name в полях модели Group совпадает с ожидаемым."""
        group = PostModelTest.group
        for field in PostModelTest.group_model_specs:
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field['field_name']).verbose_name,
                    field['verbose_name']
                )

    def test_group_help_texts(self):
        """help_text в полях модели Group совпадает с ожидаемым."""
        group = PostModelTest.group
        for field in PostModelTest.group_model_specs:
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field['field_name']).help_text,
                    field['help_text']
                )

    def test_post_model_have_correct_object_names(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        post = PostModelTest.post
        expected_post_name = post.text[:15]
        self.assertEqual(expected_post_name, str(post))

    def test_post_verbose_names(self):
        """verbose_name в полях модели Post совпадает с ожидаемым."""
        post = PostModelTest.post
        for field in PostModelTest.post_model_specs:
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field['field_name']).verbose_name,
                    field['verbose_name']
                )

    def test_post_help_texts(self):
        """help_text в полях модели Post совпадает с ожидаемым."""
        post = PostModelTest.post
        for field in PostModelTest.post_model_specs:
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field['field_name']).help_text,
                    field['help_text']
                )
