from collections import defaultdict
from django.utils import timezone
from datetime import datetime, date
import calendar

from django.shortcuts import redirect, render
from django.db.models import Sum
from .models import PeopleDirectory, Loan
from django.db import models
from django.contrib import messages

import plotly.colors as pc
import plotly.graph_objects as go
import random
from django.db.models import Sum
from django.db.models.functions import TruncMonth, TruncDay
from .models import Record, Category, CategoryGroup
from django.core.paginator import Paginator

from .utils_form import TimestampFilterForm


datetime_local_format = "%Y-%m-%dT%H:%M"
date_format = "%d/%m/%Y"
item_per_page = 10


def getDailyRecord(records):
    grouped_records = defaultdict(list)
    for record in records:
        date_key = record.timestamp.strftime(date_format)
        grouped_records[date_key].append(record)

    daily_records = list(grouped_records.items())

    return daily_records


def getLoan(loans, collects):
    total_money_grouped = loans.values("lender_borrower").annotate(
        total_money=Sum("money")
    )

    result_list = []
    for item in total_money_grouped:
        lender_borrower_id = item["lender_borrower"]
        total_money = formatMoney(item["total_money"])
        lender_borrower = PeopleDirectory.objects.get(id=lender_borrower_id)

        lends_borrows = loans.filter(lender_borrower__id=lender_borrower_id)
        collects_repaids = collects.filter(lender_borrower__id=lender_borrower_id)
        calculate = getLoanTotal(lends_borrows, collects_repaids)

        result_list.append(
            {
                "lender_borrower": lender_borrower,
                "total_money": total_money,
                "calculate": calculate,
            }
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
    need_collect_repaid = (
        total_money - total_collect_repaid
        if total_money - total_collect_repaid > 0
        else 0
    )
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
            messages.success(req, "Sửa thành công.")

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


def get_page(query, req):
    p = Paginator(query, item_per_page)
    page = req.GET.get("page")
    return p.get_page(page)


def renderLoanDetail(req, id, loanForm, type):
    category1 = "Cho vay"
    category2 = "Thu nợ"
    redirect_to = "lend_detail"
    page_info = {
        "title": "Chi Tiết Khoản Vay",
        "item_name": "Bản ghi",
    }

    lender_borrower = PeopleDirectory.objects.get(id=id)

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
    query = Loan.objects.filter(
        models.Q(category__name=category1) | models.Q(category__name=category2),
        lender_borrower__id=id,
        wallet__author=req.user,
    )

    loans = get_page(query, req)

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
            messages.success(req, "Thêm Vay Nợ thành công.")
            return redirect(redirect_to, id)

    ctx = {
        "form": form,
        "loan_detail": loan_detail,
        "calculate": calculate,
        "lender_borrower": lender_borrower,
        "paginator": loans,
        "page_info": page_info,
    }
    return render(req, "loan/loan-detail.html", ctx)


def total_report(req, type=CategoryGroup.INCOME):
    today = date.today()
    last_day_of_month = calendar.monthrange(today.year, today.month)[1]

    start_of_month = datetime(today.year, today.month, 1)
    end_of_month = datetime(today.year, today.month, last_day_of_month)
    start_of_year = datetime(today.year, 1, 1)
    end_of_year = datetime(today.year, 12, 31)

    total_today = (
        Record.objects.filter(
            timestamp__date=today,
            wallet__author=req.user,
            wallet__is_calculate=True,
            category__in=Category.objects.filter(
                models.Q(is_default=True) | models.Q(author=req.user),
                category_group=type,
            ),
        ).aggregate(total_money=Sum("money"))["total_money"]
        or 0
    )

    total_this_month = (
        Record.objects.filter(
            timestamp__range=(start_of_month, end_of_month),
            wallet__author=req.user,
            wallet__is_calculate=True,
            category__in=Category.objects.filter(
                models.Q(is_default=True) | models.Q(author=req.user),
                category_group=type,
            ),
        ).aggregate(total_money=Sum("money"))["total_money"]
        or 0
    )

    total_this_year = (
        Record.objects.filter(
            timestamp__range=(start_of_year, end_of_year),
            wallet__author=req.user,
            wallet__is_calculate=True,
            category__in=Category.objects.filter(
                models.Q(is_default=True) | models.Q(author=req.user),
                category_group=type,
            ),
        ).aggregate(total_money=Sum("money"))["total_money"]
        or 0
    )

    return {
        "today": total_today,
        "this_month": total_this_month,
        "this_year": total_this_year,
    }


def get_months_report(req, p="m"):
    year = datetime.now().year
    incomes = None
    spendings = None

    incomes = (
        Record.objects.filter(
            wallet__author=req.user,
            wallet__is_calculate=True,
            timestamp__year=year,
            category__in=Category.objects.filter(
                models.Q(is_default=True) | models.Q(author=req.user),
                category_group=CategoryGroup.INCOME,
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
                category_group=CategoryGroup.SPENDING,
            ),
        )
        .annotate(month_year=TruncMonth("timestamp"))
        .values("month_year")
        .annotate(total_money=Sum("money"))
        .order_by("month_year")
    )

    months_incomes = [f"Thg {data['month_year'].strftime('%m')}" for data in incomes]
    total_incomes = [data["total_money"] for data in incomes]

    months_spendings = [
        f"Thg {data['month_year'].strftime('%m')}" for data in spendings
    ]
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
        plot_bgcolor="white",
        # xaxis=dict(range=[1, 12])
    )

    return fig.to_html(include_plotlyjs=False, full_html=False)


def get_bar_chart_day_report(req):
    today = date.today()
    last_day_of_month = calendar.monthrange(today.year, today.month)[1]
    start_of_month = datetime(today.year, today.month, 1)
    end_of_month = datetime(today.year, today.month, last_day_of_month)

    incomes = (
        Record.objects.filter(
            wallet__author=req.user,
            wallet__is_calculate=True,
            timestamp__range=(start_of_month, end_of_month),
            category__in=Category.objects.filter(
                models.Q(is_default=True) | models.Q(author=req.user),
                category_group=CategoryGroup.INCOME,
            ),
        )
        .annotate(day=TruncDay("timestamp"))
        .values("day")
        .annotate(total_money=Sum("money"))
        .order_by("day")
    )
    spendings = (
        Record.objects.filter(
            wallet__author=req.user,
            wallet__is_calculate=True,
            timestamp__range=(start_of_month, end_of_month),
            category__in=Category.objects.filter(
                models.Q(is_default=True) | models.Q(author=req.user),
                category_group=CategoryGroup.SPENDING,
            ),
        )
        .annotate(day=TruncDay("timestamp"))
        .values("day")
        .annotate(total_money=Sum("money"))
        .order_by("day")
    )

    days_incomes = [f"{data['day'].strftime('%d')}" for data in incomes]
    total_incomes = [data["total_money"] for data in incomes]

    days_spendings = [f"{data['day'].strftime('%d')}" for data in spendings]
    total_spendings = [data["total_money"] for data in spendings]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=days_incomes,
            y=total_incomes,
            name="Thu Nhập",
            marker=dict(color="rgb(25, 135, 84)"),
        )
    )
    fig.add_trace(
        go.Bar(
            x=days_spendings,
            y=total_spendings,
            name="Chi Tiêu",
            marker=dict(color="rgb(220, 53, 69)"),
        )
    )

    fig.update_layout(
        barmode="group",
        title=f"<b>Tình hình Thu Chi tháng {today.month}/{today.year}</b>",
        xaxis_title="<b>Ngày</b>",
        title_x=0.5,
        plot_bgcolor="white",
    )

    return fig.to_html(include_plotlyjs=False, full_html=False)


def get_pie_chart_report(req, p="m"):
    incomes = None
    spendings = None
    p_label = "tháng này"
    today = date.today()
    if p == "m":
        last_day_of_month = calendar.monthrange(today.year, today.month)[1]
        start_of_month = datetime(today.year, today.month, 1)
        end_of_month = datetime(today.year, today.month, last_day_of_month)

        incomes = Record.objects.filter(
            wallet__author=req.user,
            wallet__is_calculate=True,
            category__category_group=CategoryGroup.INCOME,
            timestamp__range=(start_of_month, end_of_month),
        )
        spendings = Record.objects.filter(
            wallet__author=req.user,
            wallet__is_calculate=True,
            category__category_group=CategoryGroup.SPENDING,
            timestamp__range=(start_of_month, end_of_month),
        )
    else:
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = datetime.combine(today, datetime.max.time())
        today_range = (start_of_day, end_of_day)
        p_label = "hôm nay"

        incomes = Record.objects.filter(
            wallet__author=req.user,
            wallet__is_calculate=True,
            category__category_group=CategoryGroup.INCOME,
            timestamp__range=today_range,
        )
        spendings = Record.objects.filter(
            wallet__author=req.user,
            wallet__is_calculate=True,
            category__category_group=CategoryGroup.SPENDING,
            timestamp__range=today_range,
        )

    print(spendings)
    colors = ["#{:06x}".format(random.randint(0, 0xFFFFFF)) for _ in range(50)]

    return {
        "incomes": pie_chart(incomes, f"Thu Nhập {p_label}", colors).to_html(
            include_plotlyjs=False, full_html=False
        ),
        "spendings": pie_chart(spendings, f"Chi Tiêu {p_label}", colors[::-1]).to_html(
            include_plotlyjs=False, full_html=False
        ),
    }


def pie_chart(reports, title, colors):
    categories = reports.values("category__name").annotate(
        total_money=models.Sum("money")
    )
    labels = [category["category__name"] for category in categories]
    values = [category["total_money"] for category in categories]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                marker_colors=colors,
                # marker_colors=pc.sequential.Inferno_r,
            )
        ]
    )

    fig.update_traces(textposition="inside")
    fig.update_layout(
        title=f"<b>{title}</b>", uniformtext_minsize=12, uniformtext_mode="hide"
    )

    return fig


def get_categories(query):
    result = defaultdict(list)

    for category in query:
        category_group = CategoryGroup(category.category_group).label
        number_of_records = Record.objects.filter(category=category).count()

        result[category_group].append(category)
        # print(category.updatedAt)

    return dict(result)


def get_filter(req, query, group=CategoryGroup.INCOME):
    filter_form = TimestampFilterForm(user=req.user, c_group=group)
    f_start = req.GET.get("f")
    f_end = req.GET.get("t")
    f_categories = req.GET.getlist("c")
    initial = {}

    if f_start and f_end:
        query = query.filter(timestamp__range=(f_start, f_end))
        initial.update({"f": f_start, "t": f_end})

    if f_categories:
        query = query.filter(category__id__in=f_categories)
        initial.update({"c": f_categories})

    if initial:
        filter_form = TimestampFilterForm(user=req.user, initial=initial, c_group=group)

    return {"query": query, "form": filter_form}
