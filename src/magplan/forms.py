from collections import namedtuple

from django import forms
from django.forms import ModelForm
from django_ace import AceWidget

from magplan.models import Idea, Post, Comment, Section, Issue, User, Profile

SelectChoice = namedtuple('SelectChoice', ['slug', 'title'])
IDEA_AUTHOR_SELF_CHOICE = SelectChoice('SELF', 'Напишу сам')


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
        fields = (
            'l_name', 'f_name', 'n_name', 'bio', 'f_name_generic', 'l_name_generic', 'bio_generic', 'notes',
        )
        widgets = {
            'l_name': forms.TextInput(attrs={'class': 'form-control', }),
            'f_name': forms.TextInput(attrs={'class': 'form-control', }),
            'n_name': forms.TextInput(attrs={'class': 'form-control', }),
            'bio': forms.Textarea(attrs={'class': 'form-control', }),

            'l_name_generic': forms.TextInput(attrs={'class': 'form-control', }),
            'f_name_generic': forms.TextInput(attrs={'class': 'form-control', }),
            'bio_generic': forms.Textarea(attrs={'class': 'form-control', }),

            'notes': forms.Textarea(attrs={'class': 'form-control', }),
        }

    def __init__(self, *args, **kwargs):
        super(ProfileModelForm, self).__init__(*args, **kwargs)
        for f in ('l_name', 'f_name', 'n_name', 'notes',):
            self.fields[f].required = False


class IdeaAuthorTypeChoiceField(forms.ChoiceField):
    def validate(self, value):
        """Custom field, which allows virtual SELF field value"""
        if value == IDEA_AUTHOR_SELF_CHOICE.slug:
            return

        super().validate(value)


class IdeaModelForm(ModelForm):
    # Add virtual field to extend default widget choices

    EXTENDED_AUTHOR_TYPE_CHOICES = (
        IDEA_AUTHOR_SELF_CHOICE, *reversed(Idea.AUTHOR_TYPE_CHOICES)
    )

    author_type = IdeaAuthorTypeChoiceField(
        choices=EXTENDED_AUTHOR_TYPE_CHOICES,
        widget=forms.Select(
            attrs={'class': 'form-control'},
        ),
        label=Idea._meta.get_field('author_type').verbose_name
    )

    class Meta:
        model = Idea
        fields = ['title', 'description', 'author_type', 'authors_new', 'authors']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', }),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'authors_new': forms.TextInput(attrs={'class': 'form-control'}),
            'authors': forms.SelectMultiple(attrs={
                'class': 'form-control live_multiselect',
            }),
        }

    def clean_author_type(self):
        data = self.cleaned_data['author_type']
        if data == IDEA_AUTHOR_SELF_CHOICE.slug:
            return Idea.AUTHOR_TYPE_EXISTING

        return data


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
    editor = forms.ModelChoiceField(queryset=(
        User.objects.filter(is_active=True).prefetch_related('profile').order_by('profile__l_name').all()
    ),
        label="Редактор",
        empty_label=None,
        widget=forms.Select(attrs={'class': 'form-control', 'rows': 5})
    )

    class Meta:
        model = Post
        fields = ('issues', 'editor', 'finished_at', 'published_at', 'css', 'slug')

        widgets = {
            'issues': forms.SelectMultiple(attrs={
                'class': 'form-control live_multiselect wiih_suggestions',
            }),
            'editor': forms.Select(attrs={'class': 'form-control', }),
            'finished_at': forms.DateInput(attrs={'class': 'form-control date_picker', }),
            'published_at': forms.DateInput(attrs={'class': 'form-control date_picker', }),
            'css': AceWidget(
                mode='css', theme='textmate', showinvisibles=True, toolbar=False
            ),
            'slug': forms.TextInput(attrs={'class': 'form-control', }),
        }

    def __init__(self, *args, **kwargs):
        super(PostMetaForm, self).__init__(*args, **kwargs)
        self.fields['wp_id'].required = False


class PostBaseModelForm(ModelForm):
    section = forms.ModelChoiceField(
        queryset=Section.on_current_site.filter(is_whitelisted=False, is_archived=False),
        label="Рубрика",
        empty_label=None,
        widget=forms.Select(attrs={'class': 'form-control', 'rows': 5})
    )

    class Meta:
        model = Post
        fields = ('title', 'description', 'issues', 'authors', 'finished_at', 'section',)
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', }),
            'description': forms.Textarea(attrs={'class': 'form-control', }),
            'issues': forms.SelectMultiple(attrs={
                'class': 'form-control live_multiselect wiih_suggestions',
            }),
            'authors': forms.SelectMultiple(attrs={
                'class': 'form-control live_multiselect',
            }),
            'finished_at': forms.DateInput(attrs={'class': 'form-control date_picker', }),
        }

    def __init__(self, *args, **kwargs):
        super(PostBaseModelForm, self).__init__(*args, **kwargs)
        self.fields['section'].empty_label = '---'


class PostExtendedModelForm(ModelForm):
    section = forms.ModelChoiceField(
        queryset=Section.objects.filter(is_archived=False),
        label="Рубрика",
        empty_label=None,
        widget=forms.Select(attrs={'class': 'form-control', 'rows': 5})
    )

    class Meta(PostBaseModelForm.Meta):
        model = Post

        fields = ('title', 'description', 'authors', 'kicker', 'xmd', 'section')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', }),
            'description': forms.HiddenInput(),
            'authors': forms.SelectMultiple(attrs={
                'class': 'form-control live_multiselect',
            }),
            'kicker': forms.TextInput(attrs={'class': 'form-control', }, ),
            'xmd': forms.Textarea(attrs={'class': 'form-control', 'rows': 20, }),
        }

    def __init__(self, *args, **kwargs):
        super(PostExtendedModelForm, self).__init__(*args, **kwargs)
        self.fields['kicker'].required = False
        self.fields['xmd'].required = False
        self.fields['section'].empty_label = None


class PostDirectCreateModelForm(PostBaseModelForm):
    class Meta(PostBaseModelForm.Meta):
        fields = ('title', 'issues', 'authors', 'finished_at', 'section',)


class DefaultPostModelForm(PostDirectCreateModelForm):
    pass


class ArchivedPostModelForm(PostDirectCreateModelForm):
    section = forms.ModelChoiceField(
        queryset=Section.objects.all(),
        label="Рубрика",
        empty_label=None,
        widget=forms.Select(attrs={'class': 'form-control', 'rows': 5})
    )


class WhitelistedPostExtendedModelForm(PostDirectCreateModelForm):
    section = forms.ModelChoiceField(
        queryset=Section.objects.filter(is_archived=False, is_whitelisted=True),
        label="Рубрика",
        empty_label=None,
        widget=forms.Select(attrs={'class': 'form-control', 'rows': 5})
    )


class AdPostExtendedModelForm(PostDirectCreateModelForm):
    issues = forms.ModelChoiceField(
        queryset=Issue.objects.filter(number=0),
        empty_label=None,
        widget=forms.Select(attrs={'class': 'form-control', 'rows': 5})
    )


class CommentModelForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text', ]
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }
