from django import forms
from .models import Comment
from taggit.forms import TagField
from taggit_labels.widgets import LabelWidget


class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False, widget=forms.Textarea)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'body']
        labels = {
            'name': 'Имя',
            'email': 'Электронная почта',
            'body': 'Комментарий'
        }

class ContentForm (forms.ModelForm):
    tags = TagField(required=False, widget=LabelWidget)

class SearchForm(forms.Form):
    query = forms.CharField(label='Поиск')