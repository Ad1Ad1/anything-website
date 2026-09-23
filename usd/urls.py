from django.urls import path, include

from . import views
app_name='usd'
urlpatterns = [
    #Main page of this app
    path('', views.view_usd_page, name="view_usd_page"),
    #Page to send a new membership request
    path('membership/new/', views.new_request_citizenship, name="new_request_citizenship"),
    #Page to view all membership requests as Community App Moderator
    path('membership/moderator-view/', views.view_moderator_ucr, name="view_moderator_ucr"),
    #Page to accept a membership request as Community App Moderator
    path('membership/moderator-view/<int:req>/accept/', views.accept_citizenship_request, name="accept_citizenship_request"),
    #Page to reject a membership request as Community App Moderator
    path('membership/moderator-view/<int:req>/reject/', views.reject_citizenship_request, name="reject_citizenship_request"),
    #Page to revert a membership request action as Community App Moderator
    path('membership/moderator-view/<int:req>/revert/', views.revert_citizenship_request_action, name="revert_citizenship_request_action"),
    #Page to view all Idea Requests
    path('idea-requests/', views.petitions, name="petitions"),
    #Page to create an Idea Request
    path('idea-requests/new/', views.new_petition, name="new_petition"),
    #Page to delete an Idea Request
    path('idea-requests/<int:petition_id>/delete/', views.delete_petition, name="delete_petition"),
    #Page for voting on an Idea Request
    path('idea-request/<int:petition_id>/<str:vtype>/', views.vote, name='vote'),
    #Page for viewing news
    path('news/', views.news, name='news')
]
