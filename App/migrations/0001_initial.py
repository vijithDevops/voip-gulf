# Generated by Django 2.1.2 on 2018-10-10 13:55

import datetime
from decimal import Decimal
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='balanceTransactionReport',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('category', models.CharField(blank=True, max_length=20, null=True)),
                ('date', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=20, null=True)),
                ('remarks', models.CharField(blank=True, max_length=200, null=True)),
                ('status', models.BooleanField(default=True)),
            ],
            options={
                'db_table': 'balanceTransactionReport',
            },
        ),
        migrations.CreateModel(
            name='datacardAssignments',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('margin', models.DecimalField(decimal_places=2, max_digits=20, null=True)),
            ],
            options={
                'db_table': 'datacardAssignments',
            },
        ),
        migrations.CreateModel(
            name='datacardproducts',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(blank=True, max_length=50, unique=True)),
                ('status', models.BooleanField(default=True)),
                ('cdate', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('sdate', models.DateTimeField(blank=True, null=True)),
                ('denomination', models.DecimalField(decimal_places=2, max_digits=20, null=True)),
            ],
            options={
                'db_table': 'datacardproducts',
            },
        ),
        migrations.CreateModel(
            name='dcardBrands',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('brand', models.CharField(blank=True, max_length=100, null=True)),
                ('description', models.CharField(blank=True, max_length=200, null=True)),
                ('denomination', models.DecimalField(decimal_places=2, max_digits=20)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='brands/%y%m%d')),
                ('currency', models.CharField(default='SAR', max_length=50)),
            ],
            options={
                'db_table': 'dcardBrands',
            },
        ),
        migrations.CreateModel(
            name='dcarduplogs',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('cdate', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('file', models.FileField(blank=True, null=True, upload_to='csvfiles/%y%m%d')),
                ('pcount', models.IntegerField(blank=True, null=True)),
                ('scount', models.IntegerField(blank=True, null=True)),
                ('status', models.BooleanField(default=True)),
                ('sdate', models.DateTimeField(blank=True, null=True)),
                ('brand', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dcard_brand_logdata', to='App.dcardBrands')),
            ],
            options={
                'db_table': 'dcarduplogs',
            },
        ),
        migrations.CreateModel(
            name='dcardupproducts',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('denomination', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('username', models.CharField(blank=True, max_length=50, unique=True)),
                ('status', models.BooleanField(default=True)),
                ('brand', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dcard_brand_data', to='App.dcardBrands')),
                ('fileid', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dcard_file_data', to='App.dcarduplogs')),
            ],
            options={
                'db_table': 'dcardupproducts',
            },
        ),
        migrations.CreateModel(
            name='exchangeRate',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('source', models.CharField(max_length=200)),
                ('destination', models.CharField(max_length=2000)),
                ('rate', models.DecimalField(decimal_places=2, max_digits=20, null=True)),
            ],
            options={
                'db_table': 'exchangeRate',
            },
        ),
        migrations.CreateModel(
            name='fundTransactionReport',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('role', models.CharField(blank=True, max_length=20, null=True)),
                ('date', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=20, null=True)),
                ('balance', models.DecimalField(decimal_places=2, max_digits=20, null=True)),
                ('remarks', models.CharField(blank=True, max_length=200, null=True)),
            ],
            options={
                'db_table': 'fundTransactionReport',
            },
        ),
        migrations.CreateModel(
            name='rcardAssignments',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('margin', models.DecimalField(decimal_places=2, max_digits=20, null=True)),
            ],
            options={
                'db_table': 'rcardAssignments',
            },
        ),
        migrations.CreateModel(
            name='rcardBrands',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('brand', models.CharField(blank=True, max_length=50, null=True)),
                ('description', models.CharField(blank=True, max_length=200, null=True)),
                ('denomination', models.DecimalField(decimal_places=2, max_digits=20)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='brands/%y%m%d')),
                ('currency', models.CharField(default='SAR', max_length=50)),
            ],
            options={
                'db_table': 'rcardBrands',
            },
        ),
        migrations.CreateModel(
            name='rcardProducts',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(blank=True, max_length=50, unique=True)),
                ('status', models.BooleanField(default=True)),
                ('cdate', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('sdate', models.DateTimeField(blank=True, null=True)),
                ('denomination', models.DecimalField(decimal_places=2, max_digits=20, null=True)),
                ('brand', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rcardproducts_brand_data', to='App.rcardBrands')),
            ],
            options={
                'db_table': 'rcardproducts',
            },
        ),
        migrations.CreateModel(
            name='rcarduplogs',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('cdate', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('file', models.FileField(blank=True, null=True, upload_to='csvfiles/%y%m%d')),
                ('pcount', models.IntegerField(blank=True, null=True)),
                ('scount', models.IntegerField(blank=True, null=True)),
                ('status', models.BooleanField(default=True)),
                ('sdate', models.DateTimeField(blank=True, null=True)),
                ('brand', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rcard_brand_logdata', to='App.rcardBrands')),
            ],
            options={
                'db_table': 'rcarduplogs',
            },
        ),
        migrations.CreateModel(
            name='rcardupproducts',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('denomination', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('username', models.CharField(blank=True, max_length=50, unique=True)),
                ('status', models.BooleanField(default=True)),
                ('brand', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='vcloud_brand_data', to='App.dcardBrands')),
                ('fileid', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='vcloud_file_data', to='App.dcarduplogs')),
            ],
            options={
                'db_table': 'rcardupproducts',
            },
        ),
        migrations.CreateModel(
            name='UserData',
            fields=[
                ('username', models.CharField(max_length=20, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(blank=True, max_length=50)),
                ('email', models.EmailField(max_length=254)),
                ('address', models.TextField(blank=True)),
                ('mobileno', models.CharField(blank=True, max_length=15)),
                ('postId', models.CharField(blank=True, choices=[('Admin', 'Admin'), ('Reseller', 'Reseller'), ('Sub_Reseller', 'Sub_Reseller'), ('User', 'User')], max_length=20, null=True)),
                ('status', models.BooleanField(default=True)),
                ('balance', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=20)),
                ('margin', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=20, null=True)),
                ('targetAmt', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=20, null=True)),
                ('rentalAmt', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=20, null=True)),
                ('retailerLimit', models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=20, null=True)),
                ('baseCurrency', models.CharField(blank=True, default='SAR', max_length=254)),
                ('vcloud_status', models.BooleanField(default=True)),
                ('recharge_status', models.BooleanField(default=True)),
                ('dcard_status', models.BooleanField(default=True)),
                ('rcard_status', models.BooleanField(default=True)),
                ('password', models.CharField(blank=True, max_length=500)),
                ('sponserId', models.ForeignKey(blank=True, default='No Value', null=True, on_delete=django.db.models.deletion.CASCADE, to='App.UserData')),
            ],
            options={
                'db_table': 'UserData',
            },
        ),
        migrations.CreateModel(
            name='vcloudAssignments',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('margin', models.DecimalField(decimal_places=2, max_digits=20, null=True)),
                ('assignedby', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assignedby_data', to='App.UserData')),
                ('assignedto', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assignedto_data', to='App.UserData')),
            ],
            options={
                'db_table': 'vcloudAssignments',
            },
        ),
        migrations.CreateModel(
            name='vcloudBrands',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('brand', models.CharField(blank=True, max_length=20, null=True)),
                ('description', models.CharField(blank=True, max_length=200, null=True)),
                ('denomination', models.DecimalField(decimal_places=2, max_digits=20)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='brands/%y%m%d')),
                ('currency', models.CharField(default='SAR', max_length=50)),
                ('category', models.CharField(blank=True, max_length=50)),
            ],
            options={
                'db_table': 'vcloudBrands',
            },
        ),
        migrations.CreateModel(
            name='vcloudProducts',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(blank=True, max_length=50, unique=True)),
                ('password', models.CharField(blank=True, max_length=50, unique=True)),
                ('status', models.BooleanField(default=True)),
                ('cdate', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('sdate', models.DateTimeField(blank=True, null=True)),
                ('denomination', models.DecimalField(decimal_places=2, max_digits=20, null=True)),
                ('brand', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='vcloudproducts_brand_data', to='App.vcloudBrands')),
                ('suser', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='saleduser_data', to='App.UserData')),
            ],
            options={
                'db_table': 'vcloudproducts',
            },
        ),
        migrations.CreateModel(
            name='vcloudtransactions',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('brand', models.CharField(blank=True, max_length=50)),
                ('type', models.CharField(blank=True, choices=[('Vcloud', 'Vcloud'), ('Dcard', 'Dcard'), ('Rcard', 'Rcard')], max_length=50)),
                ('brand_id', models.IntegerField(blank=True, null=True)),
                ('product_id', models.CharField(blank=True, max_length=50, null=True)),
                ('denominations', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('quantity', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('amount', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('margin1', models.DecimalField(blank=True, decimal_places=2, default=Decimal('0.00'), max_digits=20, null=True)),
                ('margin2', models.DecimalField(blank=True, decimal_places=2, default=Decimal('0.00'), max_digits=20, null=True)),
                ('margin3', models.DecimalField(blank=True, decimal_places=2, default=Decimal('0.00'), max_digits=20, null=True)),
                ('margin4', models.DecimalField(blank=True, decimal_places=2, default=Decimal('0.00'), max_digits=20, null=True)),
                ('saleduser', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='vclouduser_data', to='App.UserData')),
            ],
            options={
                'db_table': 'vcloudtransactions',
            },
        ),
        migrations.CreateModel(
            name='vclouduplogs',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('cdate', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('file', models.FileField(blank=True, null=True, upload_to='csvfiles/%y%m%d')),
                ('pcount', models.IntegerField(blank=True, null=True)),
                ('scount', models.IntegerField(blank=True, null=True)),
                ('status', models.BooleanField(default=True)),
                ('sdate', models.DateTimeField(blank=True, null=True)),
                ('brand', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='vcloud_brand_logdata', to='App.vcloudBrands')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='vcloud_uplog_data', to='App.UserData')),
            ],
            options={
                'db_table': 'vclouduplogs',
            },
        ),
        migrations.CreateModel(
            name='vcloudupproducts',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('denomination', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True)),
                ('username', models.CharField(blank=True, max_length=50, unique=True)),
                ('password', models.CharField(blank=True, max_length=50, unique=True)),
                ('status', models.BooleanField(default=True)),
                ('brand', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='vcloud_brand_data', to='App.vcloudBrands')),
                ('fileid', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='vcloud_file_data', to='App.vclouduplogs')),
            ],
            options={
                'db_table': 'vcloudupproducts',
            },
        ),
        migrations.AddField(
            model_name='vcloudassignments',
            name='brand',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='vcloudassignment_brand_data', to='App.vcloudBrands'),
        ),
        migrations.AddField(
            model_name='rcarduplogs',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rcard_uplog_data', to='App.UserData'),
        ),
        migrations.AddField(
            model_name='rcardproducts',
            name='suser',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rcardsaleduser_data', to='App.UserData'),
        ),
        migrations.AddField(
            model_name='rcardassignments',
            name='assignedby',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rcardassignedby_data', to='App.UserData'),
        ),
        migrations.AddField(
            model_name='rcardassignments',
            name='assignedto',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rcardassignedto_data', to='App.UserData'),
        ),
        migrations.AddField(
            model_name='rcardassignments',
            name='brand',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rcardassignment_brand_data', to='App.rcardBrands'),
        ),
        migrations.AddField(
            model_name='fundtransactionreport',
            name='destination',
            field=models.ForeignKey(default='No Value', on_delete=django.db.models.deletion.CASCADE, related_name='transaction_destination_data', to='App.UserData'),
        ),
        migrations.AddField(
            model_name='fundtransactionreport',
            name='source',
            field=models.ForeignKey(default='No Value', on_delete=django.db.models.deletion.CASCADE, related_name='transaction_source_data', to='App.UserData'),
        ),
        migrations.AddField(
            model_name='dcarduplogs',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dcard_uplog_data', to='App.UserData'),
        ),
        migrations.AddField(
            model_name='datacardproducts',
            name='brand',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dcardproducts_brand_data', to='App.dcardBrands'),
        ),
        migrations.AddField(
            model_name='datacardproducts',
            name='suser',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dcardsaleduser_data', to='App.UserData'),
        ),
        migrations.AddField(
            model_name='datacardassignments',
            name='assignedby',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dcardassignedby_data', to='App.UserData'),
        ),
        migrations.AddField(
            model_name='datacardassignments',
            name='assignedto',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dcardassignedto_data', to='App.UserData'),
        ),
        migrations.AddField(
            model_name='datacardassignments',
            name='brand',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='dcardassignment_brand_data', to='App.dcardBrands'),
        ),
        migrations.AddField(
            model_name='balancetransactionreport',
            name='destination',
            field=models.ForeignKey(default='No Value', on_delete=django.db.models.deletion.CASCADE, related_name='destination_data', to='App.UserData'),
        ),
        migrations.AddField(
            model_name='balancetransactionreport',
            name='source',
            field=models.ForeignKey(default='No Value', on_delete=django.db.models.deletion.CASCADE, related_name='source_data', to='App.UserData'),
        ),
        migrations.CreateModel(
            name='SaleSummary',
            fields=[
            ],
            options={
                'verbose_name': 'Sale Summary',
                'verbose_name_plural': 'Sales Summary',
                'proxy': True,
                'indexes': [],
            },
            bases=('App.vcloudtransactions',),
        ),
    ]