from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/edit/', views.edit_profile_view, name='edit_profile'),
    path('profile/<str:username>/', views.profile_view, name='profile'),
    path('profile/<str:username>/followers/', views.followers_list_view, name='followers'),
    path('profile/<str:username>/following/', views.following_list_view, name='following'),
    path('follow/<str:username>/', views.toggle_follow_view, name='toggle_follow'),
    path('follow-request/<int:follow_id>/<str:action>/', views.handle_follow_request_view, name='handle_follow_request'),
]
