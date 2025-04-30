from django.urls import path

from . import views

urlpatterns = [
    path("sync/", views.chat_sync, name="index_sync"),
]