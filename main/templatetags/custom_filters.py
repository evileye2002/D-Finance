from django import template
from ..models import CategoryGroup

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
