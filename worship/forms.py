from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Comment, User, WorshipRecord


class BootstrapMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault('class', 'form-check-input')
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault('class', 'form-select')
            else:
                field.widget.attrs.setdefault('class', 'form-control')


class RegisterForm(BootstrapMixin, UserCreationForm):
    real_name = forms.CharField(label='실명', max_length=30)

    class Meta:
        model = User
        fields = ('username', 'real_name', 'password1', 'password2')


class WorshipRecordForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = WorshipRecord
        fields = ('date', 'worship_type', 'title', 'content', 'is_shared')
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'content': forms.Textarea(attrs={'rows': 5}),
        }


class CommentForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={'rows': 2, 'placeholder': '댓글을 입력하세요...'}),
        }
        labels = {
            'content': '',
        }
