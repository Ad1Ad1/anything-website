from django.urls import path, include

from . import views
app_name='users'
urlpatterns = [
    #Add Django URL authentication
    path('', include('django.contrib.auth.urls')),
    #Banned page
    path('banned/', views.banned, name='banned'),
    #Page for registration
    path('register/', views.register, name="register"),
    #Page for logging out
    path('logged_out/', views.logged_out, name="logged_out"),
    #Page for profile showcase
    path('profile/<str:username>/<str:typer>', views.profile, name="profile"),
    #Page for completing the profile
    path('new_profile/',views.new_profile, name="new_profile"),
    #Page for editing a profile
    path('edit_profile/',views.edit_profile, name="edit_profile"),
    #Page for deleting a user
    path('delete_user/',views.delete_user, name="delete_user"),
    #Page for banning or unbanning a user
    path('ban_user/<str:target>/<str:tpe>/', views.ban_user,name="ban_user"),
    #Page for promoting a user
    path('promote_user/<str:target>/', views.promote_user,name="promote_user"),
    #Page for demoting a user
    path('demote_user/<str:target>/', views.demote_user,name="demote_user"),
    #Page for creating a style
    path('styles/new/', views.new_style, name="new_style"),
    #Page for editing a style
    path('styles/<int:style_id>/edit/', views.edit_style, name="edit_style"),
    #Page for deleting a style
    path('styles/<int:style_id>/delete/', views.delete_style, name="delete_style"),
    #Page for selecting a style
    path('styles/<int:style_id>/select/', views.select_style, name="select_style"),
    #Page for cookies, privacy policy, etc
    path('personal/', views.cookies, name="personal"),
]
