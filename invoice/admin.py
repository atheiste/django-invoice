from django.contrib import admin
from django.conf import settings
from invoice.models import Invoice, InvoiceItem, Address, BankAccount


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem


class InvoiceAdmin(admin.ModelAdmin):
    inlines = [InvoiceItemInline, ]
    search_fields = ('id', 'contractor__name', 'subscriber__name')
    list_display = (
        'id',
        'state',
        'total_amount',
        'date_issued',
        'date_paid',
    )

admin.site.register(Invoice, InvoiceAdmin)

if not hasattr(settings, "INVOICE_ADDRESS_MODEL"):
    admin.site.register(Address)

if not hasattr(settings, "INVOICE_BANK_ACCOUNT_MODEL"):
    admin.site.register(BankAccount)
