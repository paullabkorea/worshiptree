from django.urls import path

from . import views

app_name = 'worship'

urlpatterns = [
    # Auth
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),

    # Home
    path('', views.home, name='home'),

    # Worship Record CRUD
    path('record/new/', views.record_create, name='record_create'),
    path('record/<int:pk>/edit/', views.record_edit, name='record_edit'),
    path('record/<int:pk>/delete/', views.record_delete, name='record_delete'),

    # Board
    path('board/', views.board_list, name='board_list'),
    path('board/<int:pk>/', views.board_detail, name='board_detail'),

    # Comments & Likes
    path('board/<int:pk>/comment/', views.comment_create, name='comment_create'),
    path('board/<int:pk>/like/', views.like_toggle, name='like_toggle'),

    # API
    path('api/tree-data/', views.tree_data, name='tree_data'),
]
