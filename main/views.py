from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.db import models
from datetime import datetime
from django.contrib import messages

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from .models import *
from .forms import *
from .utils_form import RecordFilterForm, ReportFilterForm
from .utils import *


# Create your views here.
@login_required(login_url="sign-in")
def index(req):
    incomes = total_report(req)
    spendings = total_report(req, CategoryGroup.SPENDING)

    f = filter_report(req)
    form = f["form"]
    bar_chart_report = f["bar_chart_report"]
    pie_chart_reports = f["pie_chart_reports"]

    ctx = {
        "bar_chart_report": bar_chart_report,
        "pie_chart_reports": pie_chart_reports,
        "incomes": incomes,
        "spendings": spendings,
        "form": form,
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
    ctx = {"form": form}

    return render(req, "sign-in.html", ctx)


def sign_up(req):
    if req.user.is_authenticated:
        return redirect("index")

    form = SignUpForm()

    if req.method == "POST":
        form = SignUpForm(req.POST)
        if form.is_valid():
            form.save()
            messages.success(req, "Đăng ký Tài Khoản thành công.")
            return redirect("sign-in")

    # print(form.__getitem__("password2").errors.as_json())
    ctx = {"form": form}

    return render(req, "sign-up.html", ctx)


def sign_out(req):
    logout(req)
    return redirect("sign-in")


@login_required(login_url="sign-in")
def income(req):
    form = RecordForm(type=CategoryGroup.INCOME, user=req.user)
    page_info = {
        "title": "Thu Nhập",
        "item_name": "Khoản thu",
    }
    modal = {
        "id": "modal-add",
        "title": "Thêm Khoản Thu",
        "form": {
            "id": "form-add",
            "content": form,
            "url": "/url/2",
            "btn": [{"label": "Thêm"}],
        },
    }

    query = Record.objects.filter(
        wallet__author=req.user,
        category__in=Category.objects.filter(
            models.Q(is_default=True) | models.Q(author=req.user),
            category_group=CategoryGroup.INCOME,
        ),
    )

    f = filter_record(req, query)
    query = f["query"]
    filter_form = f["form"]

    records = get_page(query, req)
    daily_records = getDailyRecord(records)

    if req.method == "POST":
        form = RecordForm(req.POST, user=req.user, type=CategoryGroup.INCOME)
        if form.is_valid():
            income = form.save(commit=False)
            income.author = req.user
            income.save()
            messages.success(req, "Thêm Bản ghi thành công.")
            return redirect("income")

    ctx = {
        "form": form,
        "filter_form": filter_form,
        "daily_records": daily_records,
        "paginator": records,
        "page_info": page_info,
        "modal": modal,
    }

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
            messages.success(req, "Sửa Bản Ghi thành công")
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
    messages.success(req, "Xóa Bản Ghi thành công.")
    return redirect(next_url)


@login_required(login_url="sign-in")
def spending(req):
    form = RecordForm(type=CategoryGroup.SPENDING, user=req.user)
    page_info = {
        "title": "Chi Tiêu",
        "item_name": "Khoản chi",
    }
    modal = {
        "id": "modal-add",
        "title": "Thêm Khoản Chi",
        "form": {
            "id": "form-add",
            "content": form,
            "url": "/url/2",
            "btn": [{"label": "Thêm"}],
        },
    }

    query = Record.objects.filter(
        wallet__author=req.user,
        category__in=Category.objects.filter(
            models.Q(is_default=True) | models.Q(author=req.user),
            category_group=CategoryGroup.SPENDING,
        ),
    )

    f = filter_record(req, query, CategoryGroup.SPENDING)
    query = f["query"]
    filter_form = f["form"]

    records = get_page(query, req)
    daily_records = getDailyRecord(records)

    if req.method == "POST":
        form = RecordForm(req.POST, user=req.user, type=CategoryGroup.SPENDING)
        if form.is_valid():
            spending = form.save(commit=False)
            spending.author = req.user
            spending.save()
            messages.success(req, "Thêm Bản Ghi thành công.")
            return redirect("spending")

    ctx = {
        "form": form,
        "filter_form": filter_form,
        "daily_records": daily_records,
        "paginator": records,
        "page_info": page_info,
        "modal": modal,
    }

    return render(req, "record/record.html", ctx)


@login_required(login_url="sign-in")
def lend(req):
    form = LoanForm(user=req.user, type="lend")
    page_info = {
        "title": "Vay Nợ - Cho Vay",
        "item_name": "",
    }
    modal = {
        "id": "modal-add",
        "title": "Thêm Khoản Vay",
        "form": {
            "id": "form-add",
            "content": form,
            "url": "/url/2",
            "btn": [{"label": "Thêm"}],
        },
    }
    lends = Loan.objects.filter(
        wallet__in=Wallet.objects.filter(author=req.user), category__name="Cho vay"
    )
    collects = Loan.objects.filter(
        wallet__in=Wallet.objects.filter(author=req.user), category__name="Thu nợ"
    )
    loans = getLoan(lends, collects)
    calculate = getLoanTotal(lends, collects)

    if req.method == "POST":
        form = LoanForm(req.POST, user=req.user, type="lend")
        if form.is_valid():
            form.save()
            messages.success(req, "Thêm Vay Nợ thành công.")
            return redirect("lend")

    ctx = {
        "form": form,
        "loans": loans,
        "calculate": calculate,
        "page_info": page_info,
        "modal": modal,
    }

    return render(req, "loan/loan.html", ctx)


@login_required(login_url="sign-in")
def borrow(req):
    form = LoanForm(user=req.user, type="borrow")
    page_info = {
        "title": "Vay Nợ - Đi Vay",
        "item_name": "",
    }
    modal = {
        "id": "modal-add",
        "title": "Thêm Khoản Vay",
        "form": {
            "id": "form-add",
            "content": form,
            "url": "/url/2",
            "btn": [{"label": "Thêm"}],
        },
    }
    borrows = Loan.objects.filter(
        wallet__in=Wallet.objects.filter(author=req.user), category__name="Đi vay"
    )
    repaids = Loan.objects.filter(
        wallet__in=Wallet.objects.filter(author=req.user), category__name="Trả nợ"
    )
    loans = getLoan(borrows, repaids)
    calculate = getLoanTotal(borrows, repaids)

    if req.method == "POST":
        form = LoanForm(req.POST, user=req.user, type="borrow")
        if form.is_valid():
            form.save()
            messages.success(req, "Thêm Vay Nợ thành công.")
            return redirect("borrow")

    ctx = {
        "form": form,
        "loans": loans,
        "calculate": calculate,
        "page_info": page_info,
        "modal": modal,
    }
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
            messages.success(req, "Sửa Vay Nợ thành công")
            return redirect(next_url)

    ctx = {"form": form, "loan": loan, "next_url": next_url}
    return render(req, "loan/loan-change.html", ctx)


@login_required(login_url="sign-in")
def loan_delete(req, loan_id):
    next_url = req.GET.get("next")
    loan = Loan.objects.get(id=loan_id, wallet__author=req.user)
    loan.delete()
    messages.success(req, "Xóa Vay Nợ thành công.")

    return redirect(next_url)


@login_required(login_url="sign-in")
def wallet(req):
    form = WalletForm()
    page_info = {
        "title": "Ví Của Bạn",
        "item_name": "Ví",
    }
    modal = {
        "id": "modal-add",
        "title": "Thêm Ví",
        "form": {
            "id": "form-add",
            "content": form,
            "url": "/url/2",
            "btn": [{"label": "Thêm"}],
        },
    }
    query = Wallet.objects.filter(author=req.user)

    wallets = get_page(query, req)

    if req.method == "POST":
        form = WalletForm(req.POST)
        if form.is_valid():
            wallet = form.save(commit=False)
            wallet.author = req.user
            wallet.save()
            messages.success(req, "Thêm Ví thành công.")

            return redirect("wallet")

    ctx = {
        "form": form,
        "wallets": wallets,
        "paginator": wallets,
        "page_info": page_info,
        "modal": modal,
    }

    return render(req, "wallet/wallet.html", ctx)


@login_required(login_url="sign-in")
def wallet_change(req, wallet_id):
    wallet = Wallet.objects.get(id=wallet_id, author=req.user)

    return changeForm(req, "wallet", WalletForm, wallet, "wallet/wallet-change.html")


@login_required(login_url="sign-in")
def wallet_delete(req, wallet_id):
    wallet = Wallet.objects.get(id=wallet_id, author=req.user)
    wallet.delete()
    messages.success(req, "Xóa Ví thành công.")

    return redirect("wallet")


@login_required(login_url="sign-in")
def directory(req):
    form = DirectoryForm()
    page_info = {
        "title": "Danh Bạ",
        "item_name": "Danh bạ",
    }
    modal = {
        "id": "modal-add",
        "title": "Thêm Danh Bạ",
        "form": {
            "id": "form-add",
            "content": form,
            "url": "/url/2",
            "btn": [{"label": "Thêm"}],
        },
    }
    query = PeopleDirectory.objects.filter(author=req.user)

    directories = get_page(query, req)

    if req.method == "POST":
        form = DirectoryForm(req.POST)
        if form.is_valid():
            directory = form.save(commit=False)
            directory.author = req.user
            directory.save()
            messages.success(req, "Thêm Danh Bạ thành công.")

            return redirect("directory")

    ctx = {
        "form": form,
        "directories": directories,
        "paginator": directories,
        "page_info": page_info,
        "modal": modal,
    }

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
    messages.success(req, "Xóa Danh Bạ thành công.")

    return redirect("directory")


@login_required(login_url="sign-in")
def category(req):
    form = CategoryForm()
    page_info = {
        "title": "Danh Bạ",
        "item_name": "Danh bạ",
    }
    modal = {
        "id": "modal-add",
        "title": "Thêm Hạng Mục",
        "form": {
            "id": "form-add",
            "content": form,
            "url": "/url/2",
            "btn": [{"label": "Thêm"}],
        },
    }

    query = Category.objects.filter(
        models.Q(category_group=CategoryGroup.INCOME)
        | models.Q(category_group=CategoryGroup.SPENDING),
        author=req.user,
    )

    page = get_page(query, req)
    category_groups = get_categories(page)

    if req.method == "POST":
        form = CategoryForm(req.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.author = req.user
            category.is_default = False
            category.save()
            messages.success(req, "Thêm Hạng Mục thành công.")

            return redirect("category")

    ctx = {
        "form": form,
        "category_groups": category_groups,
        "paginator": page,
        "page_info": page_info,
        "modal": modal,
    }

    return render(req, "category/category.html", ctx)


@login_required(login_url="sign-in")
def category_change(req, category_id):
    category = Category.objects.get(id=category_id, author=req.user)

    if category.is_default:
        messages.error(req, "Không thể xóa hay sửa đổi Hạng Mục mặc định.")
        return redirect("category")

    return changeForm(
        req, "category", CategoryForm, category, "category/category-change.html"
    )


@login_required(login_url="sign-in")
def category_delete(req, category_id):
    category = Category.objects.get(id=category_id, author=req.user)

    if category.is_default:
        return render(req, "category/category-is-default.html")

    category.delete()
    messages.success(req, "Xóa Hạng Mục thành công.")
    return redirect("category")


@login_required(login_url="sign-in")
def user_profile(req):
    profile = UserProfile.objects.get(author=req.user)
    form = ProfileForm(user=req.user, instance=profile)

    if req.method == "POST":
        form = ProfileForm(req.POST, user=req.user, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(req, "Sửa Thông Tin Tài Khoản thành công")
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
            messages.success(req, "Thay đổi mật khẩu thành công.")

            return redirect("index")

    ctx = {"form": form}

    return render(req, "profile/change-password.html", ctx)
