from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('quote/<int:quote_id>/like/', views.like_quote, name='like_quote'),
    path('quote/<int:quote_id>/dislike/', views.dislike_quote, name='dislike_quote'),
    path('add/', views.add_quote, name='add_quote'),
    path('top/', views.top_quotes, name='top_quotes'),
]