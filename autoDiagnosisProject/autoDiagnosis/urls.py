from django.urls import path
from . import views

urlpatterns = [
    path("", views.data_list, name="data_list"),
    path("data/<int:pk>/", views.data_detail, name="data_detail"),
    path("data/new/", views.data_new, name="data_new"),
    path("data/<int:pk>/edit/", views.data_edit, name="data_edit"),
    path("data/<int:pk>/delete/", views.data_delete, name="data_delete"),
    path("train_model/", views.train_model_view, name="train_model"),
    path("diagnose/", views.diagnose_view, name="diagnose"),]
