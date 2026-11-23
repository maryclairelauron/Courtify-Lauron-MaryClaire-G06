from django.urls import path

from . import views

app_name = 'courts'

urlpatterns = [
    path('', views.court_list, name='list'),
    path('add/', views.court_create, name='create'),
    path('<int:pk>/edit/', views.court_update, name='update'),
    path('<int:pk>/delete/', views.court_delete, name='delete'),
]