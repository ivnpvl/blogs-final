from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название группы',
        help_text='Введите название группы',
        error_messages={
            'max_lenght': 'Название группы не должно превышать 200 символов',
            'unique': 'Группа с таким названием уже существует',
        },
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Уникальный идентификатор группы',
        help_text=(
            'Введите идентификатор, который будет частью URL страницы: '
            'допустимо использование латинских букв, символ тире '
            'и нижнее подчёркивание'
        ),
        error_messages={
            'unique': 'Группа с таким идентификатором уже существует',
        },
    )
    description = models.TextField(
        verbose_name='Описание группы',
        help_text=(
            'Добавьте полное описание группы, чтобы вам было проще найти '
            'единомышленников'
        ),
    )

    class Meta:
        ordering = ('title',)
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст публикации',
        help_text='Текст нового поста',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор публикации',
        help_text='Выберите автора публикации',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='Группа публикации',
        help_text='Группа, к которой будет относиться пост',
    )

    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        verbose_name='Картинка',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментарий',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
    )
    text = models.TextField(
        verbose_name='Текст комментария',
    )
    created = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации комментария',
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )

    class Meta:
        ordering = ('author',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author',
            )
        ]
