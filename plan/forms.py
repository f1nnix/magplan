from django import forms
from django.forms import ModelForm
from django_ace import AceWidget

from main.models import Idea, Post, Comment, Section, Issue, User, Profile


class UserModelForm(ModelForm):
    class Meta:
        model = User
        fields = ('email',)
        widgets = {
            'email': forms.TextInput(attrs={'class': 'form-control', }),
        }


class ProfileModelForm(ModelForm):
    class Meta:
        model = Profile
        fields = ('l_name', 'f_name', 'n_name', 'notes',)
        widgets = {
            'l_name': forms.TextInput(attrs={'class': 'form-control', }),
            'f_name': forms.TextInput(attrs={'class': 'form-control', }),
            'n_name': forms.TextInput(attrs={'class': 'form-control', }),
            'notes': forms.Textarea(attrs={'class': 'form-control', }),
        }

    def __init__(self, *args, **kwargs):
        super(ProfileModelForm, self).__init__(*args, **kwargs)
        for f in ('l_name', 'f_name', 'n_name', 'notes',):
            self.fields[f].required = False


class IdeaModelForm(ModelForm):
    class Meta:
        model = Idea
        fields = ['title', 'description', 'author_type', 'authors_new', 'authors']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', }),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'author_type': forms.Select(attrs={'class': 'form-control'}),
            'authors_new': forms.TextInput(attrs={'class': 'form-control'}),
            'authors': forms.SelectMultiple(attrs={
                'class': 'form-control live_multiselect',
                'data-url': '/admin/api/users/search',
            }),
        }


class IssueModelForm(ModelForm):
    class Meta:
        model = Issue
        fields = ('number', 'title', 'description', 'published_at',)
        widgets = {
            'number': forms.TextInput(attrs={'class': 'form-control', }),
            'title': forms.TextInput(attrs={'class': 'form-control', }),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'published_at': forms.DateInput(attrs={'class': 'form-control date_picker', }),
        }


class PostMetaForm(ModelForm):
    wp_id = forms.IntegerField(widget=forms.TextInput(attrs={'class': 'form-control', }))

    class Meta:
        model = Post
        fields = ('issues', 'editor', 'finished_at', 'published_at', 'css')
        # css = forms.CharField(widget=AceWidget)

        widgets = {
            'issues': forms.SelectMultiple(attrs={
                'class': 'form-control live_multiselect wiih_suggestions',
                'data-url': '/admin/api/issues/search',
            }),
            'editor': forms.Select(attrs={'class': 'form-control', }),
            'finished_at': forms.DateInput(attrs={'class': 'form-control date_picker', }),
            'published_at': forms.DateInput(attrs={'class': 'form-control date_picker', }),
            'css': AceWidget(
                mode='css', theme='textmate', showinvisibles=True, toolbar=False
            ),
        }

    def __init__(self, *args, **kwargs):
        super(PostMetaForm, self).__init__(*args, **kwargs)
        self.fields['wp_id'].required = False


class PostBaseModelForm(ModelForm):
    section = forms.ModelChoiceField(queryset=Section.objects.filter(is_whitelisted=False, is_archived=False),
                                     label="Рубрика",
                                     empty_label=None,
                                     widget=forms.Select(attrs={'class': 'form-control', 'rows': 5}))

    class Meta:
        model = Post
        fields = ('title', 'description', 'issues', 'authors', 'finished_at', 'section',)
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', }),
            'description': forms.Textarea(attrs={'class': 'form-control', }),
            'issues': forms.SelectMultiple(attrs={
                'class': 'form-control live_multiselect wiih_suggestions',
                'data-url': '/admin/api/issues/search',
            }),
            'authors': forms.SelectMultiple(attrs={
                'class': 'form-control live_multiselect',
                'data-url': '/admin/api/users/search',
            }),
            'finished_at': forms.DateInput(attrs={'class': 'form-control date_picker', }),
        }

    def __init__(self, *args, **kwargs):
        super(PostBaseModelForm, self).__init__(*args, **kwargs)
        self.fields['section'].empty_label = '---'


class PostExtendedModelForm(ModelForm):
    section = forms.ModelChoiceField(queryset=Section.objects.filter(is_archived=False),
                                     label="Рубрика",
                                     empty_label=None,
                                     widget=forms.Select(attrs={'class': 'form-control', 'rows': 5}))

    class Meta(PostBaseModelForm.Meta):
        model = Post

        fields = ('title', 'description', 'authors', 'kicker', 'xmd', 'section')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', }),
            'description': forms.HiddenInput(),
            'authors': forms.SelectMultiple(attrs={
                'class': 'form-control live_multiselect',
                'data-url': '/admin/api/users/search',
            }),
            'kicker': forms.TextInput(attrs={'class': 'form-control', }, ),
            'xmd': forms.Textarea(attrs={'class': 'form-control', 'rows': 20, }),
        }

    def __init__(self, *args, **kwargs):
        super(PostExtendedModelForm, self).__init__(*args, **kwargs)
        self.fields['kicker'].required = False
        self.fields['xmd'].required = False
        self.fields['section'].empty_label = None


class WhitelistedPostExtendedModelForm(PostBaseModelForm):
    section = forms.ModelChoiceField(queryset=Section.objects.filter(is_archived=False, is_whitelisted=True),
                                     label="Рубрика",
                                     empty_label=None,
                                     widget=forms.Select(attrs={'class': 'form-control', 'rows': 5}))


class AdPostExtendedModelForm(PostBaseModelForm):
    issues = forms.ModelChoiceField(queryset=Issue.objects.filter(number=0),
                                    empty_label=None,
                                    widget=forms.Select(attrs={'class': 'form-control', 'rows': 5}))


class CommentModelForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text', ]
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }
