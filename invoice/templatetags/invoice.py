# coding: utf-8

from django.template import Library
from .. import utils

register = Library()


@register.filter()
def as_currency(value):
    """Format decimal number as currency."""
    return utils.format_currency(value)
