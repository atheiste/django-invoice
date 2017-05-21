#  require django >= 1.7
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class BaseConfig(AppConfig):
    """Most basic config of invoicing app."""
    name = 'invoice'
    verbose_name = _('Invoice')
