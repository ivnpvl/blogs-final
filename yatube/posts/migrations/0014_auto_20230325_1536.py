# Generated by Django 2.2.16 on 2023-03-25 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0013_auto_20230324_2239'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='created',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата публикации комментария'),
        ),
        migrations.AlterField(
            model_name='post',
            name='pub_date',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата публикации'),
        ),
    ]