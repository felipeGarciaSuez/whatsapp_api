from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # path("send_message", views.send_message_view, name="send_message_view"),
    path("webhook", views.webhook_view, name="webhook_view"),
]
