from django.urls import path
from . import views

urlpatterns = [
    path("home", views.home, name="home"),
    path("booktoday/", views.book_today, name="book_today"),
]