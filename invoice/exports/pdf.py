# coding: utf-8
import logging

from os.path import abspath, dirname, join

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Table
from reportlab.lib.fonts import addMapping
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm

from django.utils.translation import ugettext as _
from django.utils.encoding import smart_text

from invoice.utils import format_currency, format_date
from invoice.exports import Export


logger = logging.getLogger(__name__)

STATIC_DIR = join(dirname(abspath(__file__)), "..", "static", "invoice")


def get_str(obj):
    """Return string repr. of an `obj` preferably using `as_text` method."""
    return obj.as_text() if hasattr(obj, "as_text") else str(obj)


class PdfExport(Export):
    """Prints out a invoice as a PDF document of size A4 with font embedded.

    A4 size: 21 x 29.7 cm
    """
    FONT_NAME = 'FreeSans'

    def get_content_type(self):
        """MIME type of PDF document."""
        return u'application/pdf'

    def draw(self, invoice, stream):
        """Draw the invoice into a canvas."""
        pdfmetrics.registerFont(
            TTFont('FreeSans', join(STATIC_DIR, 'FreeSans.ttf')))
        addMapping('FreeSans', 0, 0, 'FreeSans')

        self.baseline = -2 * cm

        canvas = Canvas(stream, pagesize=A4)
        canvas.setCreator("django-invoice")
        canvas.setAuthor(smart_text(invoice.contractor))
        canvas.setTitle(smart_text(invoice))

        canvas.translate(0, 29.7 * cm)
        canvas.setFont(self.FONT_NAME, 10)

        canvas.saveState()
        self.draw_header(invoice, canvas)
        canvas.restoreState()

        canvas.saveState()
        self.draw_subscriber(invoice, canvas)
        canvas.restoreState()

        canvas.saveState()
        self.draw_contractor(invoice, canvas)
        canvas.restoreState()

        canvas.saveState()
        self.draw_info(invoice, canvas)
        canvas.restoreState()

        canvas.saveState()
        self.draw_items(invoice, canvas)
        canvas.restoreState()

        canvas.saveState()
        self.draw_footer(invoice, canvas)
        canvas.restoreState()

        canvas.showPage()
        canvas.save()
        canvas = None
        self.baseline = 0

    def draw_header(self, invoice, canvas):
        """Draw the invoice header with date and ID."""
        canvas.setFillColorRGB(0.2, 0.2, 0.2)
        canvas.setFont(self.FONT_NAME, 16)
        canvas.drawString(2 * cm, self.baseline,
                          smart_text(invoice))
        canvas.drawString((21 - 6) * cm, self.baseline,
                          format_date(invoice.date_issued))
        canvas.setLineWidth(3)
        self.baseline -= 0.3 * cm
        colors = (0.9, 0.5, 0.2)
        canvas.setStrokeColorRGB(*colors)
        canvas.line(1.5 * cm, self.baseline, (21 - 1.5) * cm, self.baseline)
        self.baseline -= 1 * cm

    def draw_subscriber(self, invoice, canvas):
        """Draw subscriber in the left half of contacts table."""
        canvas.setFont(self.FONT_NAME, 13)
        canvas.setFillColorRGB(0.5, 0.5, 0.5)
        canvas.drawString(1.5 * cm, self.baseline, _("Seller"))

        canvas.setFont(self.FONT_NAME, 11)
        canvas.setFillColorRGB(0, 0, 0)
        textobject = canvas.beginText(1.5 * cm, self.baseline - .7 * cm)
        for line in get_str(invoice.subscriber).split("\n"):
            textobject.textLine(line)
        canvas.drawText(textobject)

    def draw_contractor(self, invoice, canvas):
        """Draw contractor in the right half of contacts table."""
        canvas.setFont(self.FONT_NAME, 13)
        canvas.setFillColorRGB(0.5, 0.5, 0.5)
        canvas.drawString(11.5 * cm, self.baseline, _("Billing to"))
        if invoice.logo:
            try:
                canvas.drawInlineImage(invoice.logo, (21 - 1.5 - 3) * cm,
                                       self.baseline - 1.6 * cm, 2 * cm, 2 * cm, True)
            except AttributeError:
                canvas.drawImage(invoice.logo, (21 - 1.5 - 3) * cm,
                                 self.baseline - 1.6 * cm, 2 * cm, 2 * cm, True)

        canvas.setFont(self.FONT_NAME, 11)
        canvas.setFillColorRGB(0, 0, 0)
        textobject = canvas.beginText(11.5 * cm, self.baseline - .7 * cm)
        for line in get_str(invoice.contractor).split("\n"):
            textobject.textLine(line)
        canvas.drawText(textobject)
        self.baseline = -8.3 * cm

    def draw_info(self, invoice, canvas):
        """Draw legal info between contacts table and actual items."""
        from django.conf import settings
        canvas.setStrokeColorRGB(0.9, 0.9, 0.9)
        canvas.setLineWidth(0.5)
        canvas.line(1.5 * cm, self.baseline, (21 - 1.5) * cm, self.baseline)

        self.baseline -= .7 * cm
        textobject = canvas.beginText(1.5 * cm, self.baseline)
        textobject.textLine(u"{0}: {1}".format(
            _('Date issued'), format_date(invoice.date_issued)))
        textobject.textLine(u"{0}: {1}".format(
            _('Date due'), format_date(invoice.date_due)))
        canvas.drawText(textobject)

        try:
            textobject = canvas.beginText(11.5 * cm, self.baseline)
            textobject.textLine(_("Bank account: ") + str(invoice.contractor_bank))
            if getattr(settings, "LANGUAGE_CODE", "en_US") in ("cs", "cz", "cs_CZ", "cs_SK", "sk"):
                textobject.textLine(u"{0}: {1}".format(_('Variable symbol'), invoice.uid))
            canvas.drawText(textobject)
        except:
            logger.warn("Contractor {} has no bank account".format(
                invoice.contractor))

        self.baseline -= 1.5 * cm
        if invoice.get_info():
            lines = 0
            canvas.setFontSize(9)
            textobject = canvas.beginText(1.5 * cm, self.baseline)
            for line in invoice.get_info().split("\n"):
                lines += 1
                textobject.textLine(line.strip())
            canvas.drawText(textobject)
            self.baseline -= lines * .5 * cm

    def draw_items(self, invoice, canvas):
        """Draw items into a nice table."""
        data = [[_('Description'), _('Qty'), _('Unit price'), _('Tax'), _('Total')], ]
        for item in invoice.items.all():
            data.append([
                item.description,
                item.quantity,
                format_currency(item.unit_price),
                str(item.tax) + "%",
                format_currency(item.total)
            ])
        data.append([u'', u'', u'', _('Total') + u":", format_currency(invoice.total)])
        table = Table(data, colWidths=[10 * cm, 1.2 * cm, 2.5 * cm, 1.4 * cm, 2.8 * cm])
        table.setStyle([
            ('FONT', (0, 0), (-1, -1), self.FONT_NAME),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), (0.2, 0.2, 0.2)),
            ('GRID', (0, 0), (-1, -2), 1, (0.7, 0.7, 0.7)),
            ('GRID', (-2, -1), (-1, -1), 1, (0.7, 0.7, 0.7)),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('BACKGROUND', (0, 0), (-1, 0), (0.8, 0.8, 0.8)),
        ])
        tw, th, = table.wrapOn(canvas, 15 * cm, 19 * cm)
        table.drawOn(canvas, 1.5 * cm, self.baseline - th)
        self.baseline = -26 * cm

    def draw_footer(self, invoice, canvas):
        """Draw the invoice footer."""
        if invoice.get_footer():
            textobject = canvas.beginText(1.5 * cm, self.baseline)
            for line in invoice.get_footer().split("\n"):
                textobject.textLine(line.strip())
            canvas.drawText(textobject)
