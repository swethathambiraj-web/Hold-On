from django import forms
from .models import Message


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ('text', 'media')
        widgets = {
            'text': forms.TextInput(attrs={
                'class': 'form-control message-input',
                'placeholder': 'Message...',
                'autocomplete': 'off'
            }),
            'media': forms.FileInput(attrs={
                'class': 'd-none',
                'id': 'message-media-input',
                'accept': 'image/*,video/*'
            })
        }
