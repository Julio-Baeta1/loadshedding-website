from django.urls import path, re_path

from . import views
from .views import CTPastStagesViewSet, AreaViewSet

CT_past_stages_list = CTPastStagesViewSet.as_view({'get': 'list'})
CT_past_stages_detail = CTPastStagesViewSet.as_view({'get': 'retrieve'})
user_list = AreaViewSet.as_view({'get': 'list'})
user_detail = AreaViewSet.as_view({'get': 'retrieve'})

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('profile/edit', views.edit_profile, name='edit-profile'),
    path('one/', views.selection, name='one-slots'),
    path('one-day/', views.dayslots, name='day-slots'),
    path('<str:username>/one-day/', views.dayslotsLoggedIn, name='day-slots-logged-in'),

    #API
    path('api/', views.ApiRoot.as_view(), name=views.ApiRoot.name), 
    path('api/CT-past-stages/', CT_past_stages_list , name='CT-past-stages-list'),
    path('api/CT-past-stages/<int:pk>/', CT_past_stages_detail, name='CT-past-stages-detail'),
    path('api/area/', user_list, name='area-list'),
    path('api/area/<int:pk>/', user_detail, name='area-detail')
]




