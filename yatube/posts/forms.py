from django.forms import ModelForm, ValidationError

from .models import Comment, Post


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')

        def clean_text(self):
            data = self.cleaned_data['text']
            if data.replace(' ', '') == '':
                raise ValidationError('Вы должны написать сообщение!')
            return data


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)

        def clean_text(self):
            data = self.cleaned_data['text']
            if data.replace(' ', '') == '':
                raise ValidationError('Вы должны написать комментарий!')
            return data
