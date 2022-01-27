from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name= 'grards-landing'),
    path('join/', views.join, name='grards-join'),
    path('create/', views.create, name='grards-create'),
    path('edit/', views.edit, name='grards-edit'),
    path('password/',views.password, name='grards-password'),
    path('game/<str:gameCode>/<str:userName>/', views.game, name='grards-game'),
]
