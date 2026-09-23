"""Defines URL patterns for blogs"""
from django.urls import path

from . import views

app_name="blogs"
urlpatterns=[
    #Main page
    path('', views.index, name='index'),
    #Page for top content
    path('top/', views.user_top, name='user_top'),
    #Page for topics
    path('topics/', views.topics, name='topics'),
    #Personal pages for each topic
    path('topics/<int:topic_id>/', views.topic, name='topic'),
    #Top pages for each topic
    path('topics/<int:topic_id>/top/', views.topic_top, name="topic_top"),
    #Personal pages for each blog
    path('blogs/<int:blog_id>/', views.blog, name='blog'),
    #Page for adding a new topic
    path('new_topic/', views.new_topic, name='new_topic'),
    #Page for editing a topic
    path("edit_topic/<int:topic_id>/", views.edit_topic, name='edit_topic'),
    #Path for deleting a topic
    path('delete_topic/<int:topic_id>/', views.delete_topic, name='delete_topic'),
    #Page for adding a new blog
    path('new_blog/', views.new_blog, name='new_blog'),
    #Page for editing a blog
    path('edit_blog/<int:blog_id>/', views.edit_blog, name="edit_blog"),
    #Page for deleting a blog
    path('delete_blog/<int:blog_id>/', views.delete_blog, name="delete_blog"),
    #Page for viewing settings for a blog
    path('blogs/<int:blog_id>/settings/', views.blog_settings, name="blog_settings"),
    #Page for searching for writers
    path('blogs/<int:blog_id>/writers/search/', views.search_writers, name="search_writers"),
    #Page for adding writer to a blog
    path('blogs/<int:blog_id>/add_writer/<int:user_id>/', views.add_writer, name="add_writer"),
    #Page for deleting writer from a blog
    path('blogs/<int:blog_id>/delete_writer/<int:writer_id>/', views.delete_writer, name="delete_writer"),
    #Page for promoting writer on blog to owner
    path('blogs/<int:blog_id>/promote_writer/<int:writer_id>/', views.promote_writer, name="promote_writer"),
    #Page for adding a new post
    path('blogs/<int:blog_id>/new_post/<int:comment_id>/<str:is_news>/', views.new_post, name='new_post'),
    #Page for editing a post
    path('edit_post/<int:post_id>/', views.edit_post, name='edit_post'),
    #Page for deleting a post
    path('delete_post/<int:post_id>/', views.delete_post, name='delete_post'),
    #Page for voting on a post
    path('vote_post/<int:post_id>/<str:vtype>/', views.vote, name='vote'),
    #Page for reacting on a post
    path('react/<int:post_id>/<int:reaction>/', views.react, name='react'),
    #Page for adding a reaction
    path('new_reaction/', views.new_reaction, name='new_reaction'),
    #Page for editing a reaction
    path('edit_reaction/<int:react_id>/', views.edit_reaction, name="edit_reaction"),
    #Page for deleting a reaction
    path('delete_reaction/<int:react_id>/', views.delete_reaction, name="delete_reaction"),
    #Page for subscribing to a blog or a topic
    path('subscribe/<str:obj_type>/<int:obj_id>/<str:stype>/', views.subscribe, name="subscribe"),
    #Page for viewing all subscribers on a blog or a topic
    path('<str:stype>/<int:obj_id>/subscribers/', views.subscribers, name="subscribers"),
]