from django.shortcuts import render_to_response
from invoice.models import Invoice


def index(request):
    return render_to_response("index.html", {"invoices": Invoice.objects.all()})
