# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-30 13:12
from __future__ import unicode_literals

import django.db.models.deletion

from django.db import migrations, models
from django.conf import settings

from invoice import app_settings


class Migration(migrations.Migration):

    initial = False

    dependencies = [
        ('invoice', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        migrations.swappable_dependency(app_settings.ADDRESS_MODEL),
        migrations.swappable_dependency(app_settings.BANK_ACCOUNT_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='contractor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=app_settings.ADDRESS_MODEL)
        ),
        migrations.AddField(
            model_name='invoice',
            name='contractor_bank',
            field=models.ForeignKey(blank=True, db_index=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=app_settings.BANK_ACCOUNT_MODEL)
        ),
        migrations.AddField(
            model_name='invoice',
            name='subscriber',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to=app_settings.ADDRESS_MODEL)
        ),
        migrations.AddField(
            model_name='invoice',
            name='subscriber_shipping',
            field=models.ForeignKey(blank=True, db_index=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=app_settings.ADDRESS_MODEL)
        ),
        migrations.AddField(
            model_name='invoiceitem',
            name='invoice',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='invoice.Invoice')
        ),
    ]