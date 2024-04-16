from django import template
from ..models import CategoryGroup
from django.contrib.humanize.templatetags.humanize import naturaltime

register = template.Library()


@register.filter
def sum_money(records):
    result = sum(record.money for record in records)
    return "{:,}".format(result)


@register.filter
def formated(money):
    output = "{:,}".format(money) if money != None else 0
    return output


@register.filter
def category_label(input):
    label = None
    for choice in CategoryGroup.choices:
        if choice[0] == input:
            label = choice[1]
            break
    return label


@register.filter
def is_loans_has_completed(loans):
    result = False
    for loan in loans:
        if loan["calculate"]["complete_percent"] >= 100:
            result = True
            break

    return result


@register.filter
def is_over_day(value):
    result = naturaltime(value)
    if not "trước" in result:
        return True

    return False


@register.filter
def natural_time(value):
    result = naturaltime(value)
    if "trước" in result or "vừa" in result:
        return result

    replacement_dict = {
        "ago": "trước",
        "day": "ngày",
        "week": "tuần",
        "month": "tháng",
        "hour": "giờ",
        "minute": "phút",
        "second": "giây",
        "s": "",
    }

    if "," in result:
        result = result.split(",")[0] + " trước"

    for old_str, new_str in replacement_dict.items():
        result = result.replace(old_str, new_str)

    return result
