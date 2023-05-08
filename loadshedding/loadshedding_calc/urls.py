from django.urls import path

from . import views

#app_name = "loadshedding_calc"

urlpatterns = [
    #path("", views.IndexView.as_view(), name="index"),
    path("", views.index, name="index"),
    path("<int:slot_id>/", views.detail, name="detail"),
]



