from django.urls import path
from . import views

app_name = 'feed'

urlpatterns = [
    path('', views.home_feed_view, name='home'),
    path('explore/', views.explore_view, name='explore'),
    path('search/', views.search_view, name='search'),
]
