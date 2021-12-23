from django.urls import path
from . import views

app_name = 'writes-api'

urlpatterns = [
    path('', views.writes, name="writes"),
    path('create/', views.create_write, name="write-create"),
    path('edit/<str:pk>/', views.edit_write, name="write-edit"),
    path('details/<str:pk>/', views.write_details, name="write-details"),
    path('rewrite/', views.rewrite, name="write-rewrite"),
    path('vote/', views.update_vote, name="posts-vote"),
    path('delete/<str:pk>/', views.delete_write, name="delete-write"),
    path('<str:pk>/comments/', views.write_comments, name="write-comments"),
]
