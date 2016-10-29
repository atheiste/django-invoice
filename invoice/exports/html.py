# coding: utf-8

from __future__ import absolute_import

from django.template.loader import render_to_string

from . import Export


class HtmlExport(Export):
    """Basic HTML exporter class."""

    def get_content_type(self):
        """MIME type of exported document."""
        return u'text/html'

    def draw(self, invoice, stream):
        """Stream out rendered document as bytes."""
        stream.write(
            render_to_string("invoice/invoice.html", {"invoice": invoice}).encode("utf-8"))
