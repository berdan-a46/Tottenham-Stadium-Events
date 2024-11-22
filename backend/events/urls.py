from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("concurrent",views.concurrent, name="test"),
    
]