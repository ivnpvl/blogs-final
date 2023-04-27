import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post

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
class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='TestUser')
        cls.not_author = User.objects.create(username='TestNotAuthor')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.author,
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)
        cls.profile_url = reverse(
            'posts:profile', kwargs={'username': cls.author.username}
        )
        cls.post_detail_url = reverse(
            'posts:post_detail', kwargs={'post_id': cls.post.id}
        )
        cls.post_edit_url = reverse(
            'posts:post_edit', kwargs={'post_id': cls.post.id}
        )
        cls.post_commet_url = reverse(
            'posts:add_comment', kwargs={'post_id': cls.post.id}
        )
        cls.post_form_data = {
            'create': {
                'text': 'Необходимо добавить этот пост!',
                'group': cls.group.id,
                'image': SimpleUploadedFile(
                    name='create_small.gif',
                    content=SMALL_GIF,
                    content_type='image/gif',
                ),
            },
            'author_edit': {
                'text': 'Необходимо изменить этот пост!',
                'group': cls.group.id,
                'image': SimpleUploadedFile(
                    name='edit_small.gif',
                    content=SMALL_GIF,
                    content_type='image/gif',
                ),
            },
            'not_author_edit': {
                'text': 'Только автор может редактировать пост!',
            },

        }
        cls.comment_form_data = {'text': 'Тестовый комментарий'}

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_post_create_with_valid_form(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        response = PostFormTest.author_client.post(
            reverse('posts:create_post'),
            data=PostFormTest.post_form_data['create'],
            follow=True,
        )
        self.assertRedirects(response, PostFormTest.profile_url)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=PostFormTest.post_form_data['create']['text'],
                author=PostFormTest.author,
                group=PostFormTest.post_form_data['create']['group'],
                image='posts/create_small.gif',
            ).exists()
        )

    def test_post_edit_with_valid_form_from_author(self):
        """Валидная форма от автора редактирует имеющуюся запись в Post."""
        posts_count = Post.objects.count()
        response = self.author_client.post(
            PostFormTest.post_edit_url,
            data=PostFormTest.post_form_data['author_edit'],
            follow=True,
        )
        self.assertRedirects(response, PostFormTest.post_detail_url)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(
            Post.objects.filter(
                text=PostFormTest.post_form_data['author_edit']['text'],
                author=PostFormTest.author,
                group=PostFormTest.post_form_data['author_edit']['group'],
                image='posts/edit_small.gif',
            ).exists()
        )

    def test_post_edit_redirect_not_author_and_dont_edit_post(self):
        """Форма не от автора не редактирует имеющуюся запись в Post."""
        posts_count = Post.objects.count()
        response = self.not_author_client.post(
            PostFormTest.post_edit_url,
            data=PostFormTest.post_form_data['not_author_edit'],
            follow=True,
        )
        self.assertRedirects(response, PostFormTest.post_detail_url)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertFalse(
            Post.objects.filter(
                text=PostFormTest.post_form_data['not_author_edit']['text'],
            ).exists()
        )

    def test_comment_add_with_valid_form(self):
        "Валидная форма создаёт комментарий к нужному посту."
        comments_count = Comment.objects.filter(post=PostFormTest.post).count()
        response = self.author_client.post(
            PostFormTest.post_commet_url,
            data=PostFormTest.comment_form_data,
            follow=True,
        )
        self.assertRedirects(response, PostFormTest.post_detail_url)
        self.assertEqual(
            Comment.objects.filter(post=PostFormTest.post).count(),
            comments_count + 1
        )
        self.assertTrue(
            Comment.objects.filter(
                post=PostFormTest.post,
                author=PostFormTest.author,
                text=PostFormTest.comment_form_data['text'],
            ).exists()
        )
