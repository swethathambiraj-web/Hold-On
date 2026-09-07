from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('create/', views.post_create_view, name='post_create'),
    path('<int:pk>/', views.post_detail_view, name='post_detail'),
    path('<int:pk>/edit/', views.post_edit_view, name='post_edit'),
    path('<int:pk>/delete/', views.post_delete_view, name='post_delete'),
    path('<int:pk>/like/', views.toggle_like_view, name='toggle_like'),
    path('<int:pk>/save/', views.toggle_save_view, name='toggle_save'),
    path('<int:pk>/comment/', views.add_comment_view, name='add_comment'),
    path('comment/<int:pk>/delete/', views.delete_comment_view, name='delete_comment'),
    path('tags/<str:tag_name>/', views.hashtag_posts_view, name='hashtag_posts'),
]
