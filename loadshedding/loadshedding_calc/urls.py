from django.urls import path

from . import views

#app_name = "loadshedding_calc"

urlpatterns = [
    path('', views.index, name="index"),
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    #path('profile/', views.UserProfileView, name='user-profile'),
    path('one/', views.selection, name='one-slots'),
    path('day/', views.dayslots, name='day-slots'),
]



