# Generated by Django 2.2.19 on 2023-02-18 09:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0008_auto_20230218_1148'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='description',
            field=models.TextField(help_text='Добавьте полное описание группы, чтобы вам было проще найти единомышленников.', verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=models.SlugField(error_messages={'unique': 'Группа с таким идентификатором уже существует.'}, help_text='Введите идентификатор, который будет частью URL страницы. Допустимо использование латинских букв, символ тире и нижнее подчёркивание.', unique=True, verbose_name='Уникальный идентификатор'),
        ),
        migrations.AlterField(
            model_name='post',
            name='author',
            field=models.ForeignKey(help_text='Выберите автора публикации', on_delete=django.db.models.deletion.CASCADE, related_name='posts', to=settings.AUTH_USER_MODEL, verbose_name='Автор публикации'),
        ),
        migrations.AlterField(
            model_name='post',
            name='group',
            field=models.ForeignKey(blank=True, help_text='Укажите к какой группе относится публикация. Оставьте пустым, если подходящей группы нет.', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='posts', to='posts.Group', verbose_name='Группа публикации'),
        ),
        migrations.AlterField(
            model_name='post',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации'),
        ),
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(help_text='Всё, чем хотите поделиться!', verbose_name='Текст публикации'),
        ),
    ]
