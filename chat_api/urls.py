from django.urls import path

from . import views

urlpatterns = [
    # path("", views.index, name="index"),
    # path("token", views.obtener_token_csrf, name="obtener_token_csrf"),
    path("webhook", views.webhook_view, name="webhook_view"),
]
