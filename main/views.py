from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .forms import SignUpForm, SignInForm, RecordForm, WalletForm
from .models import Wallet, Record, Category


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
        category__category_group__name="Thu tiền",
        category__author=req.user,
    )
    form = RecordForm(type="income", user=req.user)

    if req.method == "POST":
        form = RecordForm(req.POST, user=req.user, type="income")
        if form.is_valid():
            income = form.save(commit=False)
            income.author = req.user
            income.save()
            return redirect("income")

    ctx = {"form": form, "records": records}

    return render(req, "income/income.html", ctx)


@login_required(login_url="sign-in")
def record_change(req, record_id):
    record = Record.objects.get(
        id=record_id, wallet__in=Wallet.objects.filter(author=req.user)
    )
    form = RecordForm(instance=record)

    if req.method == "POST":
        form = RecordForm(req.POST, instance=record)

        if form.is_valid():
            form.save()
            return redirect("index")

    ctx = {"form": form, "record": record}
    return render(req, "record/record-change.html", ctx)


@login_required(login_url="sign-in")
def record_delete(req, record_id):
    record = Record.objects.get(
        id=record_id, wallet__in=Wallet.objects.filter(author=req.user)
    )
    record.delete()
    return redirect("income")


@login_required(login_url="sign-in")
def spending(req):

    return render(req, "spending/spending.html")


@login_required(login_url="sign-in")
def loan(req):

    return render(req, "loan/loan.html")


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
    form = WalletForm(instance=wallet)

    if req.method == "POST":
        form = WalletForm(req.POST, instance=wallet)

        if form.is_valid():
            form.save()
            return redirect("wallet")

    ctx = {"form": form, "wallet": wallet}
    return render(req, "wallet/wallet-change.html", ctx)


@login_required(login_url="sign-in")
def wallet_delete(req, wallet_id):
    wallet = Wallet.objects.get(id=wallet_id, author=req.user)
    wallet.delete()
    return redirect("wallet")
