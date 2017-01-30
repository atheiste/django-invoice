"""Invoice app settings."""


class AppSettings(object):
    """App settings."""

    def __init__(self, prefix):
        """Init APP_LABEL.

        Here we can also perform logical check-ups of settings.
        """
        self.prefix = prefix if prefix.endswith("_") else (prefix + "_")

    @property
    def APP_LABEL(self):
        """The settings prefix."""
        return self.prefix[:-1]

    def _setting(self, attr, default=None):
        """Get `attr` from global settings prefixed with app_label."""
        from django.conf import settings
        return getattr(settings, self.prefix + attr, default)

    @property
    def BANK_ACCOUNT_MODEL(self):
        """Get default BankAccount model."""
        return self._setting("BANK_ACCOUNT_MODEL", "invoice.BankAccount")

    @property
    def ADDRESS_MODEL(self):
        """Get default Address model."""
        return self._setting("ADDRESS_MODEL", "invoice.Address")

    @property
    def EXPORT(self):
        """Get default Export class.

        Available shortcuts 'html' and 'pdf' are possible. Otherwise full dotted
        path to the class has to be specified.
        """
        exporter = self._setting("EXPORT", "html")
        exporter_class = self._setting("EXPORT_CLASS", None)
        if exporter_class is not None:
            return exporter_class
        return dict(
            pdf="invoice.exports.pdf.PdfExport",
            html="invoice.exports.html.HtmlExport").get(exporter, exporter)

    @property
    def UID_LENGTH(self):
        """Get default Address model."""
        from django.utils.translation import gettext as _
        uid_len = self._setting("UID_LENGTH", 6)
        assert 3 < uid_len < 10, _("INVOICE_UID_LENGTH has to be within interval (3, 10)")
        return uid_len


# Ugly? Guido recommends this himself ...
# http://mail.python.org/pipermail/python-ideas/2012-May/014969.html
import sys  # noqa
app_settings = AppSettings('INVOICE')
app_settings.__name__ = __name__
sys.modules[__name__] = app_settings
