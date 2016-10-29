# coding: utf-8
import locale
import logging

from django.db import models
from django.core import exceptions
from django.conf import settings
from importlib import import_module


def format_currency(amount, symbol=True):
    """Format `amount` as a string with current locale settings."""
    try:
        return locale.currency(amount, symbol, grouping=True)
    except ValueError as error:
        # if no locale is set use settings.LANG or default locale for monetary strings
        logging.getLogger("invoice").warn(error)
        locale_str = getattr(settings, "LANG", ".".join(locale.getlocale()))
        if not hasattr(settings, "LANG"):
            logging.getLogger("invoice").warn(
                "Using default locale {}! Alter with settings.LANG.".format(locale_str))
        locale.setlocale(locale.LC_ALL, locale_str)
    return locale.currency(amount, symbol, grouping=True)


def format_date(date):
    """Format date as a string with respect to current locale."""
    if "%" not in settings.SHORT_DATE_FORMAT:
        actual_date_format = "".join("%" + c if c.isalpha() else c
                                     for c in settings.SHORT_DATE_FORMAT)
        return date.strftime(actual_date_format)
    return date.strftime(settings.SHORT_DATE_FORMAT)


def load_class(class_path, setting_name=None):
    """Load a class given a class_path.

    The setting value may be a string or a tuple. The setting_name parameter is
    only there for pretty error output, and therefore is optional
    """
    try:
        class_module, class_name = class_path.rsplit('.', 1)
    except ValueError:
        if setting_name:
            txt = '%s isn\'t a valid module. Check your %s setting' % (
                class_path, setting_name)
        else:
            txt = '%s isn\'t a valid module.' % class_path
        raise exceptions.ImproperlyConfigured(txt)

    try:
        mod = import_module(class_module)
    except ImportError as e:
        if setting_name:
            txt = 'Error importing backend %s: "%s". Check your %s setting' % (
                class_module, e, setting_name)
        else:
            txt = 'Error importing backend %s: "%s".' % (class_module, e)
        raise exceptions.ImproperlyConfigured(txt)

    try:
        clazz = getattr(mod, class_name)
    except AttributeError:
        if setting_name:
            txt = ('Backend module "%s" does not define a "%s" class. Check'
                   ' your %s setting' % (class_module, class_name, setting_name))
        else:
            txt = 'Backend module "%s" does not define a "%s" class.' % (
                class_module, class_name)
        raise exceptions.ImproperlyConfigured(txt)
    return clazz


def model_to_dict(instance, exclude=()):
    """Transform model class into dictionary where keys are field names."""
    data = {}
    for f in instance._meta.fields:
        if exclude and f.name in exclude:
            continue
        if isinstance(f, models.ManyToManyField):
            continue
        data[f.name] = f.value_from_object(instance)
    return data
