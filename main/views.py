from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import models
from .forms import (
    SignUpForm,
    SignInForm,
    RecordForm,
    WalletForm,
    LoanForm,
    DirectoryForm,
    CategoryForm,
)
from .models import Wallet, Record, Category, PeopleDirectory, Loan
from .utils import getDailyRecord, getTotalByMonth, changeForm


# Create your views here.
def test(req):
    return render(req, "test-up.html")


@login_required(login_url="sign-in")
def index(req):
    return render(req, "index.html")


def sign_in(req):
    if req.user.is_authenticated:
        return redirect("index")

    form = SignInForm()

    if req.method == "POST":
        form = SignInForm(req, data=req.POST)
        if form.is_valid():
            username = req.POST.get("username")
            password = req.POST.get("password")
            remember = req.POST.get("remember")
            user = authenticate(req, username=username, password=password)

            if user is not None:
                if remember == "on":
                    req.session.set_expiry(60 * 60 * 24 * 30)  # 1 month
                else:
                    req.session.set_expiry(60 * 60 * 24)  # 1 day

                login(req, user)
                return redirect("index")

    print(form.errors.as_json())
    ctx = {"signInForm": form, "errors": form.non_field_errors()}

    return render(req, "sign-in.html", ctx)


def sign_up(req):
    if req.user.is_authenticated:
        return redirect("index")

    form = SignUpForm()

    if req.method == "POST":
        form = SignUpForm(req.POST)
        if form.is_valid():
            form.save()
            return redirect("sign-in")

    print(form.__getitem__("password2").errors.as_json())
    ctx = {"signUpForm": form}

    return render(req, "sign-up.html", ctx)


def sign_out(req):
    logout(req)
    return redirect("sign-in")


@login_required(login_url="sign-in")
def income(req):
    records = Record.objects.filter(
        wallet__in=Wallet.objects.filter(author=req.user),
        category__in=Category.objects.filter(
            models.Q(is_default=True) | models.Q(author=req.user),
            category_group__name="Thu tiền",
        ),
    )

    sorted_records = records.order_by("timestamp")
    daily_records = getDailyRecord(sorted_records)
    form = RecordForm(type="income", user=req.user)

    if req.method == "POST":
        form = RecordForm(req.POST, user=req.user, type="income")
        if form.is_valid():
            income = form.save(commit=False)
            income.author = req.user
            income.save()
            return redirect("income")

    ctx = {"form": form, "daily_records": daily_records}

    return render(req, "record/income/income.html", ctx)


@login_required(login_url="sign-in")
def record_change(req, record_id):
    record = Record.objects.get(
        id=record_id, wallet__in=Wallet.objects.filter(author=req.user)
    )
    ctx = changeForm("record", req, RecordForm, record)

    return render(req, "record/record-change.html", ctx)


@login_required(login_url="sign-in")
def record_delete(req, record_id):
    record = Record.objects.get(
        id=record_id, wallet__in=Wallet.objects.filter(author=req.user)
    )
    record.delete()
    return redirect("/")


@login_required(login_url="sign-in")
def spending(req):
    records = Record.objects.filter(
        wallet__in=Wallet.objects.filter(author=req.user),
        category__in=Category.objects.filter(
            models.Q(is_default=True) | models.Q(author=req.user),
            category_group__name="Chi tiền",
        ),
    )
    sorted_records = records.order_by("timestamp")
    daily_records = getDailyRecord(sorted_records=sorted_records)
    form = RecordForm(type="spending", user=req.user)

    if req.method == "POST":
        form = RecordForm(req.POST, user=req.user, type="spending")
        if form.is_valid():
            spending = form.save(commit=False)
            spending.author = req.user
            spending.save()
            return redirect("spending")

    ctx = {"form": form, "daily_records": daily_records}

    return render(req, "record/spending/spending.html", ctx)


@login_required(login_url="sign-in")
def loan(req):
    loans = Loan.objects.filter(
        wallet__in=Wallet.objects.filter(author=req.user),
        category__in=Category.objects.filter(category_group__name="Vay nợ"),
    )
    form = LoanForm(user=req.user)

    if req.method == "POST":
        form = LoanForm(req.POST, user=req.user)
        if form.is_valid():
            form.save()
            return redirect("loan")

    ctx = {"form": form, "loans": loans}

    return render(req, "loan/loan.html", ctx)


@login_required(login_url="sign-in")
def wallet(req):
    wallets = Wallet.objects.filter(author=req.user)
    form = WalletForm()

    if req.method == "POST":
        form = WalletForm(req.POST)
        if form.is_valid():
            wallet = form.save(commit=False)
            wallet.author = req.user
            wallet.save()
            return redirect("wallet")

    ctx = {"wallets": wallets, "form": form}

    return render(req, "wallet/wallet.html", ctx)


@login_required(login_url="sign-in")
def wallet_change(req, wallet_id):
    wallet = Wallet.objects.get(id=wallet_id, author=req.user)
    ctx = changeForm("wallet", req, WalletForm, wallet)

    return render(req, "wallet/wallet-change.html", ctx)


@login_required(login_url="sign-in")
def wallet_delete(req, wallet_id):
    wallet = Wallet.objects.get(id=wallet_id, author=req.user)
    wallet.delete()

    return redirect("wallet")


@login_required(login_url="sign-in")
def directory(req):
    directories = PeopleDirectory.objects.filter(author=req.user)
    form = DirectoryForm()

    if req.method == "POST":
        form = DirectoryForm(req.POST)
        if form.is_valid():
            directory = form.save(commit=False)
            directory.author = req.user
            directory.save()
            return redirect("directory")

    ctx = {"form": form, "directories": directories}

    return render(req, "directory/directory.html", ctx)


@login_required(login_url="sign-in")
def directory_change(req, directory_id):
    directory = PeopleDirectory.objects.get(id=directory_id, author=req.user)
    ctx = changeForm("directory", req, DirectoryForm, directory)

    return render(req, "directory/directory-change.html", ctx)


@login_required(login_url="sign-in")
def directory_delete(req, directory_id):
    directory = directory.objects.get(id=directory_id, author=req.user)
    directory.delete()

    return redirect("directory")


@login_required(login_url="sign-in")
def category(req):
    categories = Category.objects.filter(
        models.Q(is_default=True) | models.Q(author=req.user),
    )
    form = CategoryForm()

    if req.method == "POST":
        form = CategoryForm(req.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.author = req.user
            category.is_default = False
            category.save()
            return redirect("category")

    ctx = {"form": form, "categories": categories}

    return render(req, "category/category.html", ctx)


@login_required(login_url="sign-in")
def category_change(req, category_id):
    category = Category.objects.get(id=category_id, author=req.user)

    if category.is_default:
        return render(req, "category/category-is-default.html")

    form = CategoryForm(instance=category)
    if req.method == "POST":
        form = CategoryForm(req.POST, instance=category)

        if form.is_valid():
            form.save()
            return redirect("category")

    ctx = {"form": form, "category": category}
    return render(req, "category/category-change.html", ctx)


@login_required(login_url="sign-in")
def category_delete(req, category_id):
    category = category.objects.get(id=category_id, author=req.user)

    if category.is_default:
        return render(req, "category/category-is-default.html")

    category.delete()
    return redirect("category")
