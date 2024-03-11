from collections import defaultdict
from django.utils import timezone
from datetime import datetime,date
from django.shortcuts import redirect, render
from django.db.models import Sum
from .models import PeopleDirectory, Loan
from django.db import models

import plotly.graph_objects as go
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from datetime import datetime
from .models import Record, Category

datetime_local_format = "%Y-%m-%dT%H:%M"
date_format = "%d/%m/%Y"


def getDailyRecord(records):
    grouped_records = defaultdict(list)
    for record in records:
        date_key = record.timestamp.strftime(date_format)
        grouped_records[date_key].append(record)

    daily_records = list(grouped_records.items())

    return daily_records


def getLoan(loans):
    total_money_grouped = loans.values("lender_borrower").annotate(
        total_money=Sum("money")
    )

    result_list = []
    for item in total_money_grouped:
        lender_borrower_id = item["lender_borrower"]
        total_money = formatMoney(item["total_money"])
        lender_borrower = PeopleDirectory.objects.get(id=lender_borrower_id)
        result_list.append(
            {"lender_borrower": lender_borrower, "total_money": total_money}
        )

    return result_list


def getLoanTotal(loans, collect_repaid):
    result_list = {}
    total_money = (
        loans.aggregate(total_money=Sum("money"))["total_money"] if loans else 0
    )
    total_collect_repaid = (
        collect_repaid.aggregate(total_collect_repaid=Sum("money"))[
            "total_collect_repaid"
        ]
        if collect_repaid
        else 0
    )
    need_collect_repaid = total_money - total_collect_repaid
    complete_percent = (
        total_collect_repaid / total_money * 100 if total_money > 0 else 0
    )

    result_list = {
        "total_money": formatMoney(total_money),
        "total_collect_repaid": formatMoney(total_collect_repaid),
        "need_collect_repaid": formatMoney(need_collect_repaid),
        "complete_percent": round(complete_percent),
    }

    return result_list


def formatMoney(money):
    output = "{:,}".format(money) if money != None else 0
    return output


def getTotal(daily_records, filter):
    filter_records = [
        records for date_key, records in daily_records if date_key.endswith(filter)
    ]
    total_money = sum(record.money for records in filter_records for record in records)

    return formatMoney(total_money)


def changeForm(req, url_name, form_class, instance, render_file):
    form = form_class(instance=instance)

    if req.method == "POST":
        form = form_class(req.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect(url_name)

    ctx = {"form": form, "instance": instance}
    return render(req, render_file, ctx)


def append_log(sender, instance, created, type):
    if not hasattr(instance, "author") and not hasattr(instance, "wallet"):
        return

    log_name = timezone.now().strftime("%d-%m-%Y")
    current_time = timezone.now().strftime("%d/%b/%Y %H:%M:%S")
    user = instance.author if hasattr(instance, "author") else instance.wallet.author
    action = "đã xóa"

    if type == "save":
        action = "đã thêm" if created else "đã sửa"

    log = f'[{current_time}] {user} {action} "{instance}" ==> {sender.__name__}'

    print(log)
    with open(f"logs/{log_name}.txt", "a", encoding="utf-8") as file:
        file.write("\n" + log)


def renderLoanDetail(req, id, loanForm, type):
    category1 = "Cho vay"
    category2 = "Thu nợ"
    redirect_to = "lend_detail"

    if "borrow" in type:
        category1 = "Đi vay"
        category2 = "Trả nợ"
        redirect_to = "borrow_detail"

    lends_borrows = Loan.objects.filter(
        lender_borrower__id=id,
        wallet__author=req.user,
        category__name=category1,
    )
    collects_repaids = Loan.objects.filter(
        lender_borrower__id=id,
        wallet__author=req.user,
        category__name=category2,
    )
    loans = Loan.objects.filter(
        models.Q(category__name=category1) | models.Q(category__name=category2),
        lender_borrower__id=id,
        wallet__author=req.user,
    )
    loan_detail = getDailyRecord(loans)
    calculate = getLoanTotal(lends_borrows, collects_repaids)
    form = loanForm(user=req.user, type=type, lender_borrower_id=id)

    if req.method == "POST":
        form = loanForm(
            req.POST,
            user=req.user,
            type=type,
            lender_borrower_id=id,
        )
        if form.is_valid():
            form.save()
            return redirect(redirect_to, id)

    ctx = {"form": form, "loan_detail": loan_detail, "calculate": calculate}
    return render(req, "loan/loan-detail.html", ctx)


def total_report(req,type="Thu tiền"):
    today = date.today()
    start_of_month = datetime(today.year, today.month, 1)
    end_of_month = datetime(today.year, today.month, 31)
    start_of_year = datetime(today.year, 1, 1)
    end_of_year = datetime(today.year, 12, 31)
    
    total_today = Record.objects.filter(
        timestamp__date=today,
        wallet__author=req.user,
        wallet__is_calculate=True,
        category__in=Category.objects.filter(
            models.Q(is_default=True) | models.Q(author=req.user),
            category_group__name=type,
        )
    ).aggregate(total_money=Sum('money'))['total_money'] or 0

    total_this_month = Record.objects.filter(
        timestamp__range=(start_of_month, end_of_month),
        wallet__author=req.user,
        wallet__is_calculate=True,
        category__in=Category.objects.filter(
            models.Q(is_default=True) | models.Q(author=req.user),
            category_group__name=type,
        )
    ).aggregate(total_money=Sum('money'))['total_money'] or 0

    total_this_year = Record.objects.filter(
        timestamp__range=(start_of_year, end_of_year),
        wallet__author=req.user,
        wallet__is_calculate=True,
        category__in=Category.objects.filter(
            models.Q(is_default=True) | models.Q(author=req.user),
            category_group__name=type,
        )
    ).aggregate(total_money=Sum('money'))['total_money'] or 0


    return {"today":total_today,
            "this_month":total_this_month,
            "this_year":total_this_year}


def month_report(req, year):
    incomes = (
        Record.objects.filter(
            wallet__author=req.user,
            wallet__is_calculate=True,
            timestamp__year=year,
            category__in=Category.objects.filter(
                models.Q(is_default=True) | models.Q(author=req.user),
                category_group__name="Thu tiền",
            ),
        )
        .annotate(month_year=TruncMonth("timestamp"))
        .values("month_year")
        .annotate(total_money=Sum("money"))
        .order_by("month_year")
    )
    spendings = (
        Record.objects.filter(
            wallet__author=req.user,
            wallet__is_calculate=True,
            timestamp__year=year,
            category__in=Category.objects.filter(
                models.Q(is_default=True) | models.Q(author=req.user),
                category_group__name="Chi tiền",
            ),
        )
        .annotate(month_year=TruncMonth("timestamp"))
        .values("month_year")
        .annotate(total_money=Sum("money"))
        .order_by("month_year")
    )

    months_incomes = [f"Thg {data["month_year"].strftime("%m")}" for data in incomes]
    total_incomes = [data["total_money"] for data in incomes]
    
    months_spendings = [f"Thg {data["month_year"].strftime("%m")}" for data in spendings]
    total_spendings = [data["total_money"] for data in spendings]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=months_incomes,
            y=total_incomes,
            name="Thu Nhập",
            marker=dict(color="rgb(25, 135, 84)"),
        )
    )
    fig.add_trace(
        go.Bar(
            x=months_spendings,
            y=total_spendings,
            name="Chi Tiêu",
            marker=dict(color="rgb(220, 53, 69)"),
        )
    )

    fig.update_layout(
        barmode="group",
        title=f"<b>Tình hình Thu Chi năm {year}</b>",
        xaxis_title="<b>Tháng</b>",
        title_x=0.5,
        plot_bgcolor='white',
        # xaxis=dict(range=[1, 12])
    )

    return fig
