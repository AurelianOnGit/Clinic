from django.urls import path
from . import views

app_name = 'reception'

urlpatterns = [
    path("home", views.home, name="home"),
    path("booktoday/", views.book_today, name="book_today"),
]