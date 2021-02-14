# from django.conf.urls import url
from django.urls import path

from magplan.views import (
    sections,
    stages,
    articles,
    ideas,
    authors,
    index,
    issues,
    posts,
    api,
    preferences,
)

urlpatterns = [

    path('sections/', sections.index, name='sections_index'),
    path('stages/', stages.index, name='stages_index'),

    path('ideas/<int:idea_id>/comments/', ideas.comments, name='ideas_comments'),
    path('ideas/<int:idea_id>/approve/', ideas.approve, name='ideas_approve'),
    path('ideas/<int:idea_id>/vote/', ideas.vote, name='ideas_vote'),
    path('ideas/<int:idea_id>/', ideas.show, name='ideas_show'),
    path('ideas/', ideas.index, name='ideas_index'),

    path('articles/search', articles.search, name='articles_search'),
    path('articles/default', articles.default, name='articles_default'),
    path('articles/archived', articles.archived, name='articles_archived'),
    path('articles/advert', articles.advert, name='articles_advert'),
    path('articles/whitelisted', articles.whitelisted, name='articles_whitelisted'),
    path('articles/', articles.index, name='articles_index'),

    path('issues/<int:issue_id>/', issues.show, name='issues_show'),
    path('issues/new/', issues.create, name='issues_create'),
    path('issues/', issues.index, name='issues_index'),

    path('posts/<int:post_id>/attachments/delete/', posts.attachment_delete, name='posts_attachment_delete'),
    path('posts/<int:post_id>/comments/', posts.comments, name='posts_comments'),
    path('posts/<int:post_id>/set_stage/', posts.set_stage, name='posts_set_stage'),
    path('posts/<int:post_id>/edit/', posts.edit, name='posts_edit'),
    path('posts/<int:post_id>/edit_meta/', posts.edit_meta, name='posts_edit_meta'),
    path('posts/<int:post_id>/download/', posts.download_content, name='posts_download_content'),
    path('posts/<int:post_id>/send_to_wp/', posts.send_to_wp, name='posts_send_to_wp'),
    path('posts/<int:post_id>/', posts.show, name='posts_show'),
    path('posts', posts.create, name='posts_create'),

    path('api/issues/search/', api.issues_search, name='api_issues_search'),
    path('api/users/search/', api.authors_search, name='api_authors_search'),

    path('authors/new/', authors.new, name='authors_new'),
    path('authors/<int:user_id>/edit/', authors.edit, name='authors_edit'),
    path('authors/<int:user_id>/', authors.show, name='authors_show'),
    path('authors/', authors.index, name='authors_index'),

    path('settings/', preferences.index, name='preferences_index'),



    path('', index.index, name='index_index'),
]
