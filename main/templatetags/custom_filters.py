from django import template

register = template.Library()


@register.filter
def sum_money(records):
    result = sum(record.money for record in records)
    return "{:,}".format(result)
