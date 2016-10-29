# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import gettext as _
from django.db import models, migrations
import invoice.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=60)),
                ('street', models.CharField(max_length=60)),
                ('town', models.CharField(max_length=60)),
                ('postcode', models.CharField(max_length=10)),
                ('country', models.CharField(max_length=20)),
                ('business_id', models.CharField(null=True, verbose_name='Business ID', blank=True, max_length=12)),
                ('tax_id', models.CharField(null=True, verbose_name='Tax ID', blank=True, max_length=15)),
                ('extra', models.TextField(null=True, blank=True)),
            ],
            options={
                'verbose_name_plural': _('Addresses'),
            },
        ),
        migrations.CreateModel(
            name='BankAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('prefix', models.DecimalField(null=True, verbose_name='Prefix', max_digits=15, blank=True, decimal_places=0)),
                ('number', models.DecimalField(verbose_name='Account number', decimal_places=0, max_digits=16)),
                ('bank', models.DecimalField(verbose_name='Bank code', decimal_places=0, max_digits=4)),
            ],
            options={
                'verbose_name': _('Bank account'),
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('uid', models.CharField(unique=True, max_length=10, blank=True)),
                ('logo', models.FilePathField(null=True, match='.*(png|jpg|jpeg|svg)', blank=True)),
                ('state', models.CharField(max_length=15, default='proforma',choices=[('proforma', 'Proforma'), ('invoice', 'Invoice')])),
                ('date_issued', models.DateField(auto_now_add=True)),
                ('date_due', models.DateField(default=invoice.models.in_14_days)),
                ('date_paid', models.DateField(null=True, blank=True)),
                ('created', models.DateTimeField(verbose_name='Date added', auto_now_add=True)),
                ('modified', models.DateTimeField(verbose_name='Last modified', auto_now=True)),
                ('contractor', models.ForeignKey(related_name='+', to='invoice.Address')),
                ('contractor_bank', models.ForeignKey(null=True, blank=True, to='invoice.BankAccount', related_name='+', db_index=False)),
                ('subscriber', models.ForeignKey(related_name='+', to='invoice.Address')),
                ('subscriber_shipping', models.ForeignKey(null=True, blank=True, to='invoice.Address', related_name='+', db_index=False)),
            ],
            options={
                'verbose_name': _('Invoice'),
                'ordering': ('-date_issued', 'id'),
            },
        ),
        migrations.CreateModel(
            name='InvoiceItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('description', models.CharField(max_length=100)),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('tax', models.DecimalField(max_digits=3, decimal_places=0)),
                ('quantity', models.DecimalField(default=1, decimal_places=0, max_digits=4)),
                ('invoice', models.ForeignKey(related_name='items', to='invoice.Invoice')),
            ],
            options={
                'verbose_name': _('Invoice item'),
                'ordering': ['unit_price'],
            },
        ),
    ]
