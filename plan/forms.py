from django import forms
from django.forms import ModelForm
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
        fields = ['title', 'description', ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', }),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
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


class PostBaseModelForm(ModelForm):
    # section = forms.ModelChoiceField(queryset=Section.objects.filter(is_archived=False, is_whitelisted=False),
    #                                  label="Рубрика",
    #                                  empty_label=None,
    #                                  widget=forms.Select(attrs={'class': 'form-control', 'rows': 5}))

    class Meta:
        model = Post
        fields = ('title', 'description', 'issues', 'authors', 'published_at', 'section',)
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', }),
            'description': forms.Textarea(attrs={'class': 'form-control', }),
            'section': forms.Select(attrs={'class': 'form-control', 'rows': 5}),
            'issues': forms.SelectMultiple(attrs={
                'class': 'form-control live_multiselect',
                'data-url': '/admin/api/issues/search',
            }),
            'authors': forms.SelectMultiple(attrs={
                'class': 'form-control live_multiselect',
                'data-url': '/admin/api/users/search',
            }),
            'published_at': forms.DateInput(attrs={'class': 'form-control date_picker', }),
        }

    def __init__(self, *args, **kwargs):
        super(PostBaseModelForm, self).__init__(*args, **kwargs)
        self.fields['section'].empty_label = None


class PostExtendedModelForm(ModelForm):
    wp_id = forms.IntegerField()

    class Meta(PostBaseModelForm.Meta):
        model = Post

        fields = PostBaseModelForm.Meta.fields + ('kicker', 'xmd', 'editor',)

        widgets = PostBaseModelForm.Meta.widgets.copy()
        widgets.update({
            'kicker': forms.TextInput(attrs={'class': 'form-control', }, ),
            'xmd': forms.Textarea(attrs={'class': 'form-control', 'rows': 20, }),
            'editor': forms.Select(attrs={'class': 'form-control', }),
            'wp_id': forms.TextInput(attrs={'class': 'form-control', }),
        })

    def __init__(self, *args, **kwargs):
        super(PostExtendedModelForm, self).__init__(*args, **kwargs)
        self.fields['kicker'].required = False
        self.fields['wp_id'].required = False
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

    # class Meta(PostExtendedModelForm.Meta):
    #     widgets = PostExtendedModelForm.Meta.widgets.copy()
    #     widgets.update({
    #         'issues': forms.SelectMultiple(attrs={
    #             'class': 'form-control live_multiselect',
    #             'data-url': '/admin/api/issues/search',
    #         }),
    #
    #     })
    #
    # # def __init__(self, *args, **kwargs):
    # #     super(AdPostExtendedModelForm, self).__init__(*args, **kwargs)


class CommentModelForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text', ]
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }
