# Generated by Django 2.1.2 on 2018-10-11 07:41

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='vcloudtransactions',
            name='cbalance',
            field=models.DecimalField(blank=True, decimal_places=2, default=Decimal('0.00'), max_digits=20, null=True),
        ),
        migrations.AddField(
            model_name='vcloudtransactions',
            name='obalance',
            field=models.DecimalField(blank=True, decimal_places=2, default=Decimal('0.00'), max_digits=20, null=True),
        ),
    ]
