import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Follow, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(
            username='TestUser',
            first_name='Альберт',
            last_name='Эйнштейн',
            email='albert@yandex.ru',
            is_superuser=False,
        )
        cls.follower = User.objects.create(username='Follower')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.author,
            group=cls.group,
            image=SimpleUploadedFile(
                name='small.gif',
                content=SMALL_GIF,
                content_type='image/gif',
            )
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.follower_client = Client()
        cls.follower_client.force_login(cls.follower)
        cls.group_url = reverse(
            'posts:group_list', kwargs={'slug': cls.group.slug}
        )
        cls.profile_url = reverse(
            'posts:profile', kwargs={'username': cls.author.username}
        )
        cls.post_detail_url = reverse(
            'posts:post_detail', kwargs={'post_id': cls.post.id}
        )
        cls.post_edit_url = reverse(
            'posts:post_edit', kwargs={'post_id': cls.post.id}
        )
        cls.follow_url = reverse(
            'posts:profile_follow', kwargs={'username': cls.author.username}
        )
        cls.unfollow_url = reverse(
            'posts:profile_unfollow', kwargs={'username': cls.author.username}
        )
        cls.page_names_templates = {
            reverse('posts:index'): 'posts/index.html',
            cls.group_url: 'posts/group_list.html',
            cls.profile_url: 'posts/profile.html',
            cls.post_detail_url: 'posts/post_detail.html',
            reverse('posts:create_post'): 'posts/create_post.html',
            cls.post_edit_url: 'posts/create_post.html',
        }
        cls.context_specs = {
            'author': {
                'username': cls.author.username,
                'first_name': cls.author.first_name,
                'last_name': cls.author.last_name,
                'email': cls.author.email,
                'is_superuser': cls.author.is_superuser,
            },
            'group': {
                'title': cls.group.title,
                'slug': cls.group.slug,
                'description': cls.group.description,
            },
            'post': {
                'text': cls.post.text,
                'author': cls.author,
                'group': cls.group,
                'image': cls.post.image,
            },
            'form': {
                'text': forms.fields.CharField,
                'group': forms.models.ModelChoiceField,
            },
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        super().setUp()
        cache.clear()

    def test_pages_use_correct_template(self):
        """URL-адреса используют соответствующие шаблоны."""
        for url, template in PostViewTests.page_names_templates.items():
            with self.subTest(url=url):
                response = PostViewTests.author_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_home_page_use_caching(self):
        """Кэширование корректно работает на главной странице."""
        response = PostViewTests.author_client.get(reverse('posts:index'))
        content_before_change = response.content
        Post.objects.create(
            text='Данный пост не отобразится сразу после кэширования',
            author=PostViewTests.author,
        )
        response = PostViewTests.author_client.get(reverse('posts:index'))
        self.assertEqual(response.content, content_before_change)
        cache.clear()
        response = PostViewTests.author_client.get(reverse('posts:index'))
        self.assertNotEqual(response.content, content_before_change)

    def test_group_list_show_correct_context(self):
        """В шаблон group_list корректно передаётся группа."""
        response = PostViewTests.author_client.get(PostViewTests.group_url)
        group = response.context['group']
        self.assertIsInstance(group, Group)
        for value, expected in PostViewTests.context_specs['group'].items():
            with self.subTest(value=value):
                self.assertEqual(getattr(group, value), expected)

    def test_profile_show_correct_context(self):
        """В шаблон profile корректно передаётся пользователь."""
        response = PostViewTests.author_client.get(PostViewTests.profile_url)
        author = response.context['author']
        self.assertIsInstance(author, User)
        for value, expected in PostViewTests.context_specs['author'].items():
            with self.subTest(value=value):
                self.assertEqual(getattr(author, value), expected)

    def test_post_detail_correct_context(self):
        """В шаблон post_detail корректно передаётся пост."""
        response = PostViewTests.author_client.get(
            PostViewTests.post_detail_url
        )
        post = response.context['post']
        self.assertIsInstance(post, Post)
        for value, expected in PostViewTests.context_specs['post'].items():
            with self.subTest(value=value):
                self.assertEqual(getattr(post, value), expected)

    def test_post_create_new_post_correct_context(self):
        """В шаблон post_create корректно передаётся форма при создании
        нового поста.
        """
        response = PostViewTests.author_client.get(
            reverse('posts:create_post')
        )
        form = response.context['form']
        self.assertIsInstance(form, PostForm)
        for value, expected in PostViewTests.context_specs['form'].items():
            with self.subTest(value=value):
                self.assertIsInstance(form.fields[value], expected)

    def test_post_create_edit_post_correct_context(self):
        """В шаблон post_create корректно передаётся форма и маркер is_edit
        при редактировании существующего поста.
        """
        response = PostViewTests.author_client.get(PostViewTests.post_edit_url)
        form = response.context['form']
        self.assertIsInstance(form, PostForm)
        for value, expected in PostViewTests.context_specs['form'].items():
            with self.subTest(value=value):
                self.assertIsInstance(form.fields[value], expected)
        is_edit = response.context['is_edit']
        self.assertIsInstance(is_edit, bool)
        self.assertEqual(is_edit, True)

    def test_profile_follow_create_unfollow_delete_following(self):
        """Авторизованный пользователь может подписываться на других
        пользователей и удалять их из подписок. При попытке подписаться на
        автора, на которого уже есть подписка - новая подписка не создаётся.
        """
        self.assertFalse(
            Follow.objects.filter(
                user=PostViewTests.follower,
                author=PostViewTests.author,
            ).exists()
        )
        PostViewTests.follower_client.get(PostViewTests.follow_url)
        self.assertTrue(
            Follow.objects.filter(
                user=PostViewTests.follower,
                author=PostViewTests.author,
            ).exists()
        )
        PostViewTests.follower_client.get(PostViewTests.follow_url)
        self.assertEqual(
            Follow.objects.filter(
                user=PostViewTests.follower,
                author=PostViewTests.author,
            ).count(), 1
        )
        PostViewTests.follower_client.get(PostViewTests.unfollow_url)
        self.assertFalse(
            Follow.objects.filter(
                user=PostViewTests.follower,
                author=PostViewTests.author,
            ).exists()
        )

    def test_follow_page_contain_new_post_if_following(self):
        """Новая запись пользователя появляется в ленте тех, кто на него
        подписан и не появляется в ленте тех, кто не подписан."""
        PostViewTests.follower_client.get(PostViewTests.follow_url)
        new_post = Post.objects.create(
            text='Пост отобразится в ленте только у подписчика.',
            author=PostViewTests.author,
        )
        response = PostViewTests.follower_client.get(
            reverse('posts:follow_index')
        )
        self.assertIn(new_post, response.context['page_obj'])
        response = PostViewTests.author_client.get(
            reverse('posts:follow_index')
        )
        self.assertNotIn(new_post, response.context['page_obj'])


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PaginatorViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        """Для проверки паджинатора создаём 24 поста.
        Все нечётные посты за авторством "TestUser" - 12 постов.
        Все посты, не кратные трём, в группе "Тестовая группа" - 16 постов.
        """
        super().setUpClass()
        cls.author = User.objects.create(username='TestUser')
        cls.optional_user = User.objects.create(username='OptionalUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.posts = Post.objects.bulk_create(
            Post(
                text=f'Тестовый пост № {i}',
                author=cls.author if i % 2 == 1 else cls.optional_user,
                group=cls.group if i % 3 != 0 else None,
                image=SimpleUploadedFile(
                    name=f'small_{i}.gif',
                    content=SMALL_GIF,
                    content_type='image/gif',
                ),
            ) for i in range(1, 25)
        )
        cls.group_url = reverse(
            'posts:group_list', kwargs={'slug': cls.group.slug}
        )
        cls.profile_url = reverse(
            'posts:profile', kwargs={'username': cls.author.username}
        )
        cls.second_posts = {
            named_url: {
                'text': cls.posts[second_post_index].text,
                'author': cls.posts[second_post_index].author,
                'group': cls.posts[second_post_index].group,
                'image': cls.posts[second_post_index].image,
            } for named_url, second_post_index in (
                (reverse('posts:index'), -2),
                (cls.group_url, -3),
                (cls.profile_url, -4),
            )
        }
        cls.posts_amount = {
            reverse('posts:index'): (10, 10, 4),
            cls.group_url: (10, 6),
            cls.profile_url: (10, 2),
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        super().setUp()
        cache.clear()

    def test_pages_consist_correct_posts(self):
        """На страницы в page object передаются корректные посты."""
        for url, post_values in PaginatorViewTest.second_posts.items():
            response = self.client.get(url)
            second_post = response.context['page_obj'][1]
            self.assertIsInstance(second_post, Post)
            for value, expected in post_values.items():
                with self.subTest(value=value):
                    self.assertEqual(getattr(second_post, value), expected)

    def test_pages_contains_correct_posts_amount_ten_per_page(self):
        """На страницах отображается правильное количество постов,
        разбитое по 10 постов на страницу.
        """
        for url, amount in PaginatorViewTest.posts_amount.items():
            for page, expected in enumerate(amount, 1):
                with self.subTest(page=page):
                    response = self.client.get(f'{url}?page={page}')
                    self.assertEqual(
                        len(response.context['page_obj']), expected
                    )
