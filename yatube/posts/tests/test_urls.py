from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='TestPostAuthor')
        cls.not_author = User.objects.create(username='TestPostNotAuthor')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
        )
        cls.guest_client = Client()
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)
        cls.group_url = f'/group/{cls.group.slug}/'
        cls.profile_url = f'/profile/{cls.author.username}/'
        cls.post_detail_url = f'/posts/{cls.post.id}/'
        cls.post_edit_url = f'/posts/{cls.post.id}/edit/'
        cls.post_comment_url = f'/posts/{cls.post.id}/comment/'
        cls.follow_author = f'/profile/{cls.author.username}/follow/'
        cls.unfollow_author = f'/profile/{cls.author.username}/unfollow/'
        cls.url_accessible = {
            PostURLTests.guest_client: {
                '/': HTTPStatus.OK,
                cls.group_url: HTTPStatus.OK,
                cls.profile_url: HTTPStatus.OK,
                cls.post_detail_url: HTTPStatus.OK,
                '/create/': HTTPStatus.FOUND,
                cls.post_edit_url: HTTPStatus.FOUND,
                cls.post_comment_url: HTTPStatus.FOUND,
                '/follow/': HTTPStatus.FOUND,
                cls.follow_author: HTTPStatus.FOUND,
                cls.unfollow_author: HTTPStatus.FOUND,
                '/unexisting_page/': HTTPStatus.NOT_FOUND,
            },
            PostURLTests.author_client: {
                '/': HTTPStatus.OK,
                cls.group_url: HTTPStatus.OK,
                cls.profile_url: HTTPStatus.OK,
                cls.post_detail_url: HTTPStatus.OK,
                '/create/': HTTPStatus.OK,
                cls.post_edit_url: HTTPStatus.OK,
                cls.post_comment_url: HTTPStatus.FOUND,
                '/unexisting_page/': HTTPStatus.NOT_FOUND,
                '/follow/': HTTPStatus.OK,
            },
            PostURLTests.not_author_client: {
                '/create/': HTTPStatus.OK,
                cls.post_edit_url: HTTPStatus.FOUND,
                cls.post_comment_url: HTTPStatus.FOUND,
                cls.follow_author: HTTPStatus.FOUND,
                cls.unfollow_author: HTTPStatus.FOUND,
            },
        }
        cls.login_required_urls = (
            '/create/',
            cls.post_edit_url,
            cls.post_comment_url,
            '/follow/',
            cls.follow_author,
            cls.unfollow_author,
        )
        cls.url_template_names = {
            '/': 'posts/index.html',
            cls.group_url: 'posts/group_list.html',
            cls.profile_url: 'posts/profile.html',
            cls.post_detail_url: 'posts/post_detail.html',
            cls.post_edit_url: 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
            '/unexisting_page/': 'core/404.html',
            '/follow/': 'posts/follow.html',
        }

    def setUp(self):
        super().setUp()
        cache.clear()

    def test_urls_exists_and_redirect_anonymous(self):
        """URL-адреса доступны в зависимости от авторизации,
        страница редактирования поста доступна только автору.
        """
        for user, access in PostURLTests.url_accessible.items():
            for address, expected in access.items():
                with self.subTest(address=address):
                    response = user.get(address)
                    self.assertEqual(response.status_code, expected)

    def test_login_required_urls_redirect_anonymous_to_login(self):
        """URL, доступные только авторизованным пользователям, перенаправляют
        неавторизованного пользователя на страницу авторизации.
        """
        for login_required_url in PostURLTests.login_required_urls:
            with self.subTest(login_required_url=login_required_url):
                response = PostURLTests.guest_client.get(
                    login_required_url,
                    follow=True
                )
                self.assertRedirects(
                    response,
                    f'/auth/login/?next={login_required_url}'
                )

    def test_post_edit_url_redirect_not_author_on_post_detail(self):
        """URL с редактированием поста перенаправляет пользователя на страницу
        с информацией о посте, если он не является автором поста.
        """
        response = PostURLTests.not_author_client.get(
            PostURLTests.post_edit_url,
            follow=True,
        )
        self.assertRedirects(response, PostURLTests.post_detail_url)

    def test_urls_uses_correct_template(self):
        """URL-адреса используют соответствующие шаблоны."""
        for address, template in PostURLTests.url_template_names.items():
            with self.subTest(address=address):
                response = PostURLTests.author_client.get(address)
                self.assertTemplateUsed(response, template)
