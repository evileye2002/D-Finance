from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("sign-in", views.sign_in, name="sign-in"),
    path("sign-up", views.sign_up, name="sign-up"),
    path("sign-out", views.sign_out, name="sign-out"),
    path("income", views.income, name="income"),
    path("record/<int:record_id>/change", views.record_change, name="record_change"),
    path("record/<int:record_id>/delete", views.record_delete, name="record_delete"),
    path("spending", views.spending, name="spending"),
    path("loan", views.loan, name="loan"),
    path("wallet", views.wallet, name="wallet"),
    path("wallet/<int:wallet_id>/change", views.wallet_change, name="wallet_change"),
    path("wallet/<int:wallet_id>/delete", views.wallet_delete, name="wallet_delete"),
    path("category", views.category, name="category"),
    path(
        "category/<int:category_id>/change",
        views.category_change,
        name="category_change",
    ),
    path(
        "category/<int:category_id>/delete",
        views.category_delete,
        name="category_delete",
    ),
    path("directory", views.directory, name="directory"),
    path(
        "directory/<int:directory_id>/change",
        views.directory_change,
        name="directory_change",
    ),
    path(
        "directory/<int:directory_id>/delete",
        views.directory_delete,
        name="directory_delete",
    ),
]
