from django import forms
from .models import Post, Comment


class PostCreateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('caption', 'location')
        widgets = {
            'caption': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Write a caption... Use #hashtags to increase reach!',
                'class': 'form-control form-control-lg'
            }),
            'location': forms.TextInput(attrs={
                'placeholder': 'Add location (optional)',
                'class': 'form-control'
            }),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.TextInput(attrs={
                'placeholder': 'Add a comment...',
                'class': 'form-control comment-input',
                'autocomplete': 'off',
            }),
        }
