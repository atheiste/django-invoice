# coding: utf-8


class Export(object):
    """Base exporter class."""

    def get_content_type(self):
        """Return MIME string of generated format."""
        raise NotImplementedError('Call to abstract method get_content_type')

    def draw(self, invoice, stream):
        """Stream is a binary stream where you should write your data."""
        raise NotImplementedError('Call to abstract method draw')
