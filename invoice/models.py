# coding: utf-8
from __future__ import division
import io
import os

from decimal import Decimal, ROUND_HALF_UP
from email.mime.application import MIMEApplication

from django.db import models
from django.conf import settings
from django.forms.models import model_to_dict
from django.http.response import HttpResponse
from django.utils.encoding import python_2_unicode_compatible, smart_text
from django.utils.functional import cached_property
from django.utils import timezone as tz_aware
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy as lazy_

from . import utils
from . import app_settings

ExportManager = utils.load_class(app_settings.EXPORT)


@python_2_unicode_compatible
class Address(models.Model):
    """Address to be printed to Invoice - the method `as_text` is mandatory."""
    name = models.CharField(max_length=60)
    street = models.CharField(max_length=60)
    town = models.CharField(max_length=60)
    postcode = models.CharField(max_length=10)
    country = models.CharField(max_length=20)

    business_id = models.CharField(_("Business ID"), max_length=12, null=True, blank=True)
    tax_id = models.CharField(_("Tax ID"), max_length=15, null=True, blank=True)

    extra = models.TextField(null=True, blank=True)

    class Meta:
        """State explicitely app_label."""
        app_label = "invoice"
        verbose_name = lazy_("Address")
        verbose_name_plural = lazy_("Addresses")

    def __str__(self):
        return u"{0}, {1}".format(self.name, self.street)

    def as_text(self):
        """Rich text formating mostly for debugging."""
        self_dict = model_to_dict(self)
        base = (u"{name}\n"
                u"{street}\n"
                u"{postcode} {town}".format(**self_dict))

        if self.business_id:
            business_info = u"{0}: {1}".format(_("Reg No"), self.business_id)
            tax_info = u"{0}: {1}".format(_("Tax No"), self.tax_id)
            base = u"\n".join((base, business_info, tax_info))

        if self.extra:
            base = u"\n\n".join((base, self.extra))

        return base


@python_2_unicode_compatible
class BankAccount(models.Model):
    """Bank account is mandatory for shop."""
    prefix = models.DecimalField(_('Prefix'), null=True, blank=True,
                                 max_digits=15, decimal_places=0)
    number = models.DecimalField(_('Account number'), decimal_places=0,
                                 max_digits=16)
    bank = models.DecimalField(_('Bank code'), decimal_places=0, max_digits=4)

    class Meta:
        """State explicitely app_label."""
        app_label = "invoice"
        verbose_name = lazy_("Bank account")
        verbose_name_plural = lazy_("Bank accounts")

    def __str__(self):
        if not self.prefix:
            return u"{0} / {1}".format(self.number, self.bank)
        return u"{0} - {1} / {2}".format(self.prefix, self.number, self.bank)

    def as_text(self):
        """Rich text formatting mostly for debug."""
        return u"{0}: {1}".format(_("Bank account"), smart_text(self))


class InvoiceManager(models.Manager):
    """Manager with hard-coded usual deadlines."""

    def due(self):
        """Get unpaid invoices which should have been paid."""
        return (self.get_queryset()
                    .filter(date_issued__lte=tz_aware.now().date())
                    .filter(date_paid__isnull=True)
                )
    get_due = due


@python_2_unicode_compatible
class Invoice(models.Model):
    """Base model for invoice which can be exported to different format."""
    STATE_PROFORMA = 'proforma'
    STATE_INVOICE = 'invoice'
    INVOICE_STATES = (
        (STATE_PROFORMA, _("Proforma")),
        (STATE_INVOICE, _("Invoice")),
    )

    uid = models.CharField(unique=True, max_length=10, blank=True)
    contractor = models.ForeignKey(
        app_settings.ADDRESS_MODEL, swappable=True, related_name='+')
    contractor_bank = models.ForeignKey(
        app_settings.BANK_ACCOUNT_MODEL, swappable=True, related_name='+',
        db_index=False, null=True, blank=True)

    subscriber = models.ForeignKey(
        app_settings.ADDRESS_MODEL, swappable=True, related_name='+')
    subscriber_shipping = models.ForeignKey(
        app_settings.ADDRESS_MODEL, swappable=True, related_name='+',
        db_index=False, null=True, blank=True)
    logo = models.FilePathField(match=".*(png|jpg|jpeg|svg)", null=True, blank=True)
    state = models.CharField(max_length=15, choices=INVOICE_STATES, default=STATE_PROFORMA)

    date_issued = models.DateField(auto_now_add=True)
    date_due = models.DateField(default=utils.in_14_days)
    date_paid = models.DateField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True, verbose_name=_('Date added'))
    modified = models.DateTimeField(auto_now=True, verbose_name=_('Last modified'))

    objects = InvoiceManager()
    export = ExportManager()

    class Meta:
        """State explicitely app_label and default ordering."""
        app_label = "invoice"
        verbose_name = lazy_('Invoice')
        verbose_name_plural = lazy_('Invoices')
        ordering = ('-date_issued', 'id')

    def __str__(self):
        return " ".join((smart_text(self.state_text), self.uid))

    def save(self, *args, **kwargs):
        """Generate random UID before saving."""
        if not self.uid:
            self.uid = utils.random_hash(app_settings.UID_LENGTH)
            while Invoice.objects.filter(uid=self.uid).exists():
                self.uid = utils.random_hash(app_settings.UID_LENGTH)
        return super(Invoice, self).save(*args, **kwargs)

    @property
    def state_text(self):
        """Return suitable text of Proforma/Invoice."""
        for state in self.INVOICE_STATES:
            if state[0] == self.state:
                return state[1]

    def set_paid(self):
        """Set paid to today."""
        self.date_paid = tz_aware.now().date()
        self.state = self.STATE_INVOICE
        self.save()

    def add_item(self, description, price, tax, quantity=1):
        """Shortcut for item addition.

        :param str description: Line description
        :param number price: Unit price without VAT
        :param number tax: Tax in percents (e.g. 21)
        :param int quantity: Quantity of units
        """
        if description is not None and price is not None:
            InvoiceItem.objects.create(invoice=self, description=description,
                                       unit_price=price, tax=tax,
                                       quantity=quantity)

    def total_amount(self):
        """Return total as formated string."""
        return utils.format_currency(self.total)

    @cached_property
    def total(self):
        """Compute total price using all items as decimal number."""
        return sum(item.total for item in self.items.all())

    @property
    def filename(self):
        """Deduce unique filename for export."""
        return "{0}-{1}.{2}".format(
            self.state_text,
            self.uid,
            self.export.get_content_type().rsplit("/", 2)[1])

    def get_info(self):
        """Return (multiline) string with info printed below contractor."""
        return None

    def get_footer(self):
        """Return (multiline) string with info in footer."""
        return None

    def as_file(self, basedir):
        """Export invoice into a file to `basedir`."""
        filename = os.path.join(basedir, self.filename)
        fileio = io.FileIO(filename, "w")
        self.export.draw(self, fileio)
        fileio.close()
        return filename
    export_file = as_file  # backward compatibility

    def as_bytes(self):
        """Export invoice into byte array."""
        stream = io.BytesIO()
        self.export.draw(self, stream)
        output = stream.getvalue()
        stream.close()
        return output
    export_bytes = as_bytes  # backward compatibility

    def as_attachment(self):
        """Export invoice into email attachment."""
        attachment = MIMEApplication(self.as_bytes())
        attachment.add_header("Content-Disposition", "attachment", filename=self.filename)
        return attachment
    export_attachment = as_attachment  # backward compatibility

    def as_response(self):
        """Export invoice into downloadable HTTP reponse."""
        response = HttpResponse(content_type=self.export.get_content_type())
        response['Content-Disposition'] = 'attachment; filename="{0}"'.format(self.filename)
        response.write(self.as_bytes())
        return response
    export_response = as_response  # backward compatibility


@python_2_unicode_compatible
class InvoiceItem(models.Model):
    """Item recoded on Invoice."""
    invoice = models.ForeignKey('Invoice', related_name='items', unique=False)
    description = models.CharField(max_length=100)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.DecimalField(max_digits=4, decimal_places=0, default=1)
    tax = models.DecimalField(max_digits=3, decimal_places=0, blank=False, null=False)

    class Meta:
        app_label = "invoice"
        verbose_name = lazy_("Invoice item")
        verbose_name_plural = lazy_("Invoice items")
        ordering = ['unit_price']

    @property
    def total(self):
        """Total price for all units including tax."""
        total = self.unit_price * self.quantity * (1 + self.tax / 100)
        return Decimal("{:.3f}".format(total)).quantize(Decimal('0.01'),
                                                        rounding=ROUND_HALF_UP)

    def __str__(self):
        return self.description
