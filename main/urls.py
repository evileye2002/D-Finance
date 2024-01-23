from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("test-up", views.test, name="test-up"),
    path("sign-in", views.sign_in, name="sign-in"),
    path("sign-up", views.sign_up, name="sign-up"),
    path("sign-out", views.sign_out, name="sign-out"),
    path("income", views.income, name="income"),
    path("save", views.sign_out, name="save"),
    path("rent", views.sign_out, name="rent"),
]
