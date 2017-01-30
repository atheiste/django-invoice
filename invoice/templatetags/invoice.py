# coding: utf-8
from __future__ import absolute_import

from django.template import Library
from invoice import utils

register = Library()


@register.filter()
def as_currency(value):
    """Format decimal number as currency."""
    return utils.format_currency(value)
