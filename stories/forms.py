from django import forms
from .models import Story


class StoryCreateForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = ('media', 'caption')
        widgets = {
            'caption': forms.TextInput(attrs={
                'placeholder': 'Add a caption for your story...',
                'class': 'form-control',
            }),
            'media': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
        }
