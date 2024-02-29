from collections import defaultdict
from itertools import groupby
from datetime import datetime
from django.shortcuts import redirect, render


def getDailyRecord(sorted_records):
    grouped_records = defaultdict(list)
    for record in sorted_records:
        date_key = record.timestamp.strftime("%d/%m/%Y")
        grouped_records[date_key].append(record)

    daily_records = sorted(grouped_records.items(), key=lambda x: x[0], reverse=True)

    return daily_records


def getTotalByMonth(sorted_records):
    daily_records = getDailyRecord(sorted_records)

    current_day = datetime.now().strftime("%d/%m/%Y")
    current_month = datetime.now().strftime("%m/%Y")
    current_year = datetime.now().strftime("%Y")

    return {
        "by_day": getTotal(daily_records, current_day),
        "by_month": getTotal(daily_records, current_month),
        "by_year": getTotal(daily_records, current_year),
    }


def getTotal(daily_records, filter):
    filter_records = [
        records for date_key, records in daily_records if date_key.endswith(filter)
    ]
    total_money = sum(record.money for records in filter_records for record in records)

    return "{:,}".format(total_money)


def changeForm(req, url_name, form_class, instance, render_file):
    form = form_class(instance=instance)

    if req.method == "POST":
        form = form_class(req.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect(url_name)

    ctx = {"form": form, "instance": instance}
    return render(req, render_file, ctx)
