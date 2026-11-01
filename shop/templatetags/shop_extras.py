from django import template

register = template.Library()


def format_vnd(amount: int) -> str:
    return f"{amount:,}".replace(",", ".") + "đ"


register.filter("vnd", format_vnd)
