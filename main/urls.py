from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("sign-in", views.sign_in, name="sign-in"),
    path("sign-up", views.sign_up, name="sign-up"),
    path("sign-out", views.sign_out, name="sign-out"),
    path("income", views.income, name="income"),
    path("spending", views.spending, name="spending"),
    path("loan", views.loan, name="loan"),
    path("wallet", views.wallet, name="wallet"),
    path("wallet/<int:wallet_id>/change", views.wallet_change, name="wallet_change"),
    path("wallet/<int:wallet_id>/delete", views.wallet_delete, name="wallet_delete"),
]
