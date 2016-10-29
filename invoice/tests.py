# coding: utf-8
from __future__ import absolute_import

import datetime
import os

from django import test
from invoice import models
from invoice.exports import pdf
from invoice import test_data


class InvoiceTest(test.TestCase):

    def setUp(self):
        """Load test data first."""
        self.invoice = test_data.load()

    def test_get_due(self):
        """Test due function with respect to paid/unpaid invoices."""
        self.assertEqual(models.Invoice.objects.get_due().count(), 1)

        self.invoice.set_paid()
        self.assertEqual(models.Invoice.objects.get_due().count(), 0)

    def test_get_due2(self):
        """Test due function with respect to date functions."""
        today = datetime.date.today()
        yesterday = today - datetime.timedelta(days=1)
        tomorrow = today + datetime.timedelta(days=1)

        self.invoice.date_issued = yesterday
        self.invoice.save()
        self.assertEqual(models.Invoice.objects.get_due().count(), 1)

        self.invoice.date_issued = tomorrow
        self.invoice.save()
        self.assertEqual(models.Invoice.objects.get_due().count(), 0)

    def test_default_export(self):
        """Test default (HTML) generation.

        You can see the resulting file in /tmp/Proforma-1.html by commenting out the last line.
        """
        basedir = "/tmp"
        if self.invoice.logo:
            self.assertTrue(os.path.exists(self.invoice.logo))
        filename = self.invoice.export_file(basedir)
        self.assertTrue(os.path.exists(filename))
        stats = os.stat(filename)
        self.assertTrue(stats.st_size > 10)  # the file has to contain something
        os.unlink(filename)

    def test_pdf_export(self):
        """Test PDF generation.

        You can see the resulting file in /tmp/Proforma-1.pdf by commenting out the last line.
        """
        basedir = "/tmp"
        if self.invoice.logo:
            self.assertTrue(os.path.exists(self.invoice.logo))
        self.invoice.export = pdf.PdfExport()
        filename = self.invoice.export_file(basedir)
        self.assertTrue(os.path.exists(filename))
        stats = os.stat(filename)
        self.assertTrue(stats.st_size > 10)  # the file has to contain something
        os.unlink(filename)
