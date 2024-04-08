from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import models
from datetime import datetime
from django.core.paginator import Paginator
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from .models import *
from .forms import *
from .utils import *


# Create your views here.
@login_required(login_url="sign-in")
def index(req):
    year = datetime.now().year
    month_reports = month_report(req, year)
    incomes = total_report(req)
    spendings = total_report(req, CategoryGroup.SPENDING)
    category_reports = category_report(req)

    ctx = {
        "month_reports": month_reports,
        "category_reports": category_reports,
        "incomes": incomes,
        "spendings": spendings,
    }
    return render(req, "index.html", ctx)


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

    # print(form.errors.as_json())
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

    # print(form.__getitem__("password2").errors.as_json())
    ctx = {"signUpForm": form}

    return render(req, "sign-up.html", ctx)


def sign_out(req):
    logout(req)
    return redirect("sign-in")


@login_required(login_url="sign-in")
def income(req):
    query = Record.objects.filter(
        wallet__in=Wallet.objects.filter(author=req.user),
        category__in=Category.objects.filter(
            models.Q(is_default=True) | models.Q(author=req.user),
            category_group=CategoryGroup.INCOME,
        ),
    )

    records = get_page(query, req)

    daily_records = getDailyRecord(records)
    form = RecordForm(type=CategoryGroup.INCOME, user=req.user)

    if req.method == "POST":
        form = RecordForm(req.POST, user=req.user, type=CategoryGroup.INCOME)
        if form.is_valid():
            income = form.save(commit=False)
            income.author = req.user
            income.save()
            return redirect("income")

    ctx = {"form": form, "daily_records": daily_records, "paginator": records}

    return render(req, "record/record.html", ctx)


@login_required(login_url="sign-in")
def record_change(req, record_id):
    next_url = req.GET.get("next")
    record = Record.objects.get(
        id=record_id, wallet__in=Wallet.objects.filter(author=req.user)
    )
    form = RecordForm(instance=record, user=req.user, type="change")
    if req.method == "POST":
        form = RecordForm(req.POST, instance=record, user=req.user, type="change")
        if form.is_valid():
            form.save()
            return redirect(next_url)

    ctx = {"form": form, "record": record, "next_url": next_url}

    return render(req, "record/record-change.html", ctx)


@login_required(login_url="sign-in")
def record_delete(req, record_id):
    next_url = req.GET.get("next")
    record = Record.objects.get(
        id=record_id, wallet__in=Wallet.objects.filter(author=req.user)
    )
    record.delete()
    return redirect(next_url)


@login_required(login_url="sign-in")
def spending(req):
    query = Record.objects.filter(
        wallet__author=req.user,
        category__in=Category.objects.filter(
            models.Q(is_default=True) | models.Q(author=req.user),
            category_group=CategoryGroup.SPENDING,
        ),
    )

    records = get_page(query, req)

    daily_records = getDailyRecord(records)
    form = RecordForm(type=CategoryGroup.SPENDING, user=req.user)

    if req.method == "POST":
        form = RecordForm(req.POST, user=req.user, type=CategoryGroup.SPENDING)
        if form.is_valid():
            spending = form.save(commit=False)
            spending.author = req.user
            spending.save()
            return redirect("spending")

    ctx = {"form": form, "daily_records": daily_records, "paginator": records}

    return render(req, "record/record.html", ctx)


@login_required(login_url="sign-in")
def lend(req):
    lends = Loan.objects.filter(
        wallet__in=Wallet.objects.filter(author=req.user), category__name="Cho vay"
    )
    collects = Loan.objects.filter(
        wallet__in=Wallet.objects.filter(author=req.user), category__name="Thu nợ"
    )
    loans = getLoan(lends, collects)
    calculate = getLoanTotal(lends, collects)
    form = LoanForm(user=req.user, type="lend")

    if req.method == "POST":
        form = LoanForm(req.POST, user=req.user, type="lend")
        if form.is_valid():
            form.save()
            return redirect("lend")

    ctx = {"form": form, "loans": loans, "calculate": calculate}

    return render(req, "loan/loan.html", ctx)


@login_required(login_url="sign-in")
def borrow(req):
    borrows = Loan.objects.filter(
        wallet__in=Wallet.objects.filter(author=req.user), category__name="Đi vay"
    )
    repaids = Loan.objects.filter(
        wallet__in=Wallet.objects.filter(author=req.user), category__name="Trả nợ"
    )
    loans = getLoan(borrows, repaids)
    calculate = getLoanTotal(borrows, repaids)
    form = LoanForm(user=req.user, type="borrow")

    if req.method == "POST":
        form = LoanForm(req.POST, user=req.user, type="borrow")
        if form.is_valid():
            form.save()
            return redirect("borrow")

    ctx = {"form": form, "loans": loans, "calculate": calculate}
    return render(req, "loan/loan.html", ctx)


@login_required(login_url="sign-in")
def lend_detail(req, lender_id):
    return renderLoanDetail(req, lender_id, LoanForm, "lend-detail")


@login_required(login_url="sign-in")
def borrow_detail(req, borrower_id):
    return renderLoanDetail(req, borrower_id, LoanForm, "borrow-detail")


@login_required(login_url="sign-in")
def loan_change(req, loan_id):
    next_url = req.GET.get("next")
    loan = Loan.objects.get(id=loan_id, wallet__author=req.user)
    form = LoanForm(instance=loan, user=req.user, type="change")

    if req.method == "POST":
        form = LoanForm(req.POST, instance=loan, user=req.user, type="change")
        if form.is_valid():
            form.save()
            return redirect(next_url)

    ctx = {"form": form, "loan": loan, "next_url": next_url}
    return render(req, "loan/loan-change.html", ctx)


@login_required(login_url="sign-in")
def loan_delete(req, loan_id):
    next_url = req.GET.get("next")
    loan = Loan.objects.get(id=loan_id, wallet__author=req.user)
    loan.delete()

    return redirect(next_url)


@login_required(login_url="sign-in")
def wallet(req):
    query = Wallet.objects.filter(author=req.user)
    form = WalletForm()

    wallets = get_page(query, req)

    if req.method == "POST":
        form = WalletForm(req.POST)
        if form.is_valid():
            wallet = form.save(commit=False)
            wallet.author = req.user
            wallet.save()
            return redirect("wallet")

    ctx = {"form": form, "wallets": wallets, "paginator": wallets}

    return render(req, "wallet/wallet.html", ctx)


@login_required(login_url="sign-in")
def wallet_change(req, wallet_id):
    wallet = Wallet.objects.get(id=wallet_id, author=req.user)

    return changeForm(req, "wallet", WalletForm, wallet, "wallet/wallet-change.html")


@login_required(login_url="sign-in")
def wallet_delete(req, wallet_id):
    wallet = Wallet.objects.get(id=wallet_id, author=req.user)
    wallet.delete()

    return redirect("wallet")


@login_required(login_url="sign-in")
def directory(req):
    query = PeopleDirectory.objects.filter(author=req.user)
    form = DirectoryForm()

    directories = get_page(query, req)

    if req.method == "POST":
        form = DirectoryForm(req.POST)
        if form.is_valid():
            directory = form.save(commit=False)
            directory.author = req.user
            directory.save()
            return redirect("directory")

    ctx = {"form": form, "directories": directories, "paginator": directories}

    return render(req, "directory/directory.html", ctx)


@login_required(login_url="sign-in")
def directory_change(req, directory_id):
    directory = PeopleDirectory.objects.get(id=directory_id, author=req.user)

    return changeForm(
        req, "directory", DirectoryForm, directory, "directory/directory-change.html"
    )


@login_required(login_url="sign-in")
def directory_delete(req, directory_id):
    directory = PeopleDirectory.objects.get(id=directory_id, author=req.user)
    directory.delete()

    return redirect("directory")


@login_required(login_url="sign-in")
def category(req):
    query = Category.objects.filter(author=req.user)
    form = CategoryForm()

    page = get_page(query, req)
    category_groups = get_categories(page)

    if req.method == "POST":
        form = CategoryForm(req.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.author = req.user
            category.is_default = False
            category.save()
            return redirect("category")

    ctx = {"form": form, "category_groups": category_groups, "paginator": page}

    return render(req, "category/category.html", ctx)


@login_required(login_url="sign-in")
def category_change(req, category_id):
    category = Category.objects.get(id=category_id, author=req.user)

    if category.is_default:
        return render(req, "category/category-is-default.html")

    return changeForm(
        req, "category", CategoryForm, category, "category/category-change.html"
    )


@login_required(login_url="sign-in")
def category_delete(req, category_id):
    category = Category.objects.get(id=category_id, author=req.user)

    if category.is_default:
        return render(req, "category/category-is-default.html")

    category.delete()
    return redirect("category")


@login_required(login_url="sign-in")
def user_profile(req):
    profile = UserProfile.objects.get(author=req.user)
    form = ProfileForm(user=req.user, instance=profile)

    if req.method == "POST":
        form = ProfileForm(req.POST, user=req.user, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profile")

    ctx = {"form": form}

    return render(req, "profile/profile.html", ctx)


@login_required(login_url="sign-in")
def user_password_change(req):
    form = PasswordChangeForm(req.user)

    if req.method == "POST":
        form = PasswordChangeForm(req.user, req.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(req, user)
            return redirect("index")

    ctx = {"form": form}

    return render(req, "profile/change-password.html", ctx)
