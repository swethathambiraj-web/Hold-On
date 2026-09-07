from django.urls import path
from . import views

app_name = 'stories'

urlpatterns = [
    path('create/', views.story_create_view, name='create'),
    path('user/<str:username>/json/', views.user_stories_json_view, name='user_stories_json'),
    path('<int:story_id>/view/', views.mark_story_viewed_view, name='mark_viewed'),
    path('<int:story_id>/delete/', views.story_delete_view, name='delete'),
]
