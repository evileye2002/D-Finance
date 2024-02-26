from collections import defaultdict
from itertools import groupby


def getIncome(sorted_records):
    grouped_records = defaultdict(list)
    for record in sorted_records:
        date_key = record.timestamp.strftime("%d/%m/%Y")
        grouped_records[date_key].append(record)

    daily_records = sorted(grouped_records.items(), key=lambda x: x[0], reverse=True)

    return daily_records
