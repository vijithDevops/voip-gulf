from django.db import models
from datetime import datetime
from decimal import Decimal
from django.contrib import admin
from django.utils.safestring import mark_safe

# Create your models here.

Admin, Reseller, Sub_Reseller, User= range(4)
postId = (
    ('Admin', 'Admin'),
    ('Reseller', 'Reseller'),
    ('Sub_Reseller', 'Sub_Reseller'),
    ('User', 'User')
)
type =(
    ('Vcloud', 'Vcloud'),
    ('Dcard', 'Dcard'),
    ('Rcard', 'Rcard'),
)
class UserData(models.Model):
    username = models.CharField(max_length=20,unique=True,primary_key=True)
    name = models.CharField(max_length=50,blank=True)
    email = models.EmailField(max_length=254)
    address = models.TextField(blank=True)
    mobileno = models.CharField(max_length=15,blank=True,default='No Value',null=True)
    postId = models.CharField(choices=postId,max_length=20,blank=True, null=True)
    sponserId = models.ForeignKey('self', on_delete=models.CASCADE, default='No Value', null=True, blank=True)
    status = models.BooleanField(default=True)
    balance = models.DecimalField(max_digits=20,decimal_places=2, default=Decimal('0.00'))
    margin = models.DecimalField(null=True,max_digits=20,decimal_places=2, default=Decimal('0.00'))
    targetAmt = models.DecimalField(null=True,max_digits=20,decimal_places=2, default=Decimal('0.00'))
    rentalAmt = models.DecimalField(null=True,max_digits=20,decimal_places=2, default=Decimal('0.00'))
    retailerLimit = models.DecimalField(null=True,max_digits=20,decimal_places=2, default=Decimal('0.00'))
    baseCurrency = models.CharField(max_length=254,blank=True,default='SAR')
    vcloud_status = models.BooleanField(default=True)
    recharge_status = models.BooleanField(default=True)
    dcard_status = models.BooleanField(default=True)
    rcard_status = models.BooleanField(default=True)
    password = models.CharField(max_length=500,blank=True)

    class Meta:
        db_table = "userdata"
        verbose_name_plural = "User Registration Details"

    def __str__(self):
        return self.name

class exchangeRate(models.Model):
    id = models.AutoField(primary_key=True)
    source = models.CharField(max_length=200)
    destination = models.CharField(max_length=2000)
    rate = models.DecimalField(null=True,max_digits=20,decimal_places=2)

    class Meta:
        db_table = "exchangerate"

class balanceTransactionReport(models.Model):
    id = models.AutoField(primary_key=True)
    source = models.ForeignKey('UserData',on_delete=models.CASCADE,related_name='source_data',default='No Value')
    destination = models.ForeignKey('UserData',on_delete=models.CASCADE,related_name='destination_data',default='No Value')
    category = models.CharField(max_length=20,blank=True, null=True)
    date = models.DateTimeField(default=datetime.now, blank=True)
    amount = models.DecimalField(null=True,max_digits=20,decimal_places=2)
    pbalance = models.DecimalField(null=True,max_digits=20,decimal_places=2)
    nbalance = models.DecimalField(null=True,max_digits=20,decimal_places=2)
    cramount = models.DecimalField(null=True,max_digits=20,decimal_places=2)
    remarks = models.CharField(max_length=200,blank=True, null=True)
    status = models.BooleanField(default=True)

    class Meta:
        db_table = "balancetransactionreport"
        verbose_name_plural = "Balance Transaction Report"

class fundTransactionReport(models.Model):
    id = models.AutoField(primary_key=True)
    source = models.ForeignKey('UserData',on_delete=models.CASCADE,related_name='transaction_source_data',default='No Value')
    destination = models.ForeignKey('UserData',on_delete=models.CASCADE,related_name='transaction_destination_data',default='No Value')
    obalance = models.DecimalField(null=True,max_digits=20,decimal_places=2,default=Decimal('0.00'))
    cbalance = models.DecimalField(null=True,max_digits=20,decimal_places=2,default=Decimal('0.00'))
    role = models.CharField(max_length=20,blank=True, null=True)
    date = models.DateTimeField(default=datetime.now, blank=True)
    amount = models.DecimalField(null=True,max_digits=20,decimal_places=2)
    balance = models.DecimalField(null=True,max_digits=20,decimal_places=2)
    remarks = models.CharField(max_length=200,blank=True, null=True)

    class Meta:
        db_table = "fundtransactionreport"
        verbose_name_plural = "Payment Transaction Report"

class vcloudBrands(models.Model):
    id = models.AutoField(primary_key=True)
    brand = models.CharField(max_length=20,blank=True, null=True)
    description = models.CharField(max_length=200,blank=True, null=True)
    denomination = models.DecimalField(max_digits=20,decimal_places=2)
    logo = models.ImageField(upload_to='brands/%y%m%d', blank=True, null=True)
    currency = models.CharField(max_length=50, default='SAR')
    category = models.CharField(max_length=50, blank = True)

    class Meta:
        db_table = "vcloudbrands"
        verbose_name_plural = "Vcloud Brands"

    def image_tag(self):
         return mark_safe('<img src="/media/%s" width="150" height="150" />' % (self.logo))

    def __str__(self):
        return self.brand
    #image_tag.short_description = 'Image'
    #image_tag.allow_tags = True

class vcloudProducts(models.Model):
    id = models.AutoField(primary_key=True)
    brand = models.ForeignKey('vcloudBrands',on_delete=models.CASCADE,related_name='vcloudproducts_brand_data',blank=True, null=True)
    username = models.CharField(max_length=100,blank=True, unique=True)
    password = models.CharField(max_length=100,blank=True)
    status = models.BooleanField(default=True)
    cdate = models.DateTimeField(default=datetime.now, blank=True)
    suser = models.ForeignKey('UserData',on_delete=models.CASCADE, related_name='saleduser_data', blank=True, null=True)
    sdate = models.DateTimeField(null=True, blank=True)
    denomination =  models.DecimalField(null=True,max_digits=20,decimal_places=2)
    fileid = models.ForeignKey('vclouduplogs',on_delete=models.CASCADE,blank=True, null=True)
    productstatus = models.IntegerField(blank=True, null=True, default=0)

    class Meta:
        db_table = "vcloudproducts"
        verbose_name_plural = "Vcloud Products"

class vcloudAssignments(models.Model):
    id = models.AutoField(primary_key=True)
    brand = models.ForeignKey('vcloudBrands',on_delete=models.CASCADE,related_name='vcloudassignment_brand_data',blank=True, null=True)
    assignedto = models.ForeignKey('UserData',on_delete=models.CASCADE, related_name='assignedto_data', blank=True, null=True)
    assignedby = models.ForeignKey('UserData',on_delete=models.CASCADE, related_name='assignedby_data', blank=True, null=True)
    margin = models.DecimalField(null=True,max_digits=20,decimal_places=2)

    class Meta:
        db_table = "vcloudassignments"
        verbose_name_plural = "Vcloud Assignments Report"


class dcardBrands(models.Model):
    id = models.AutoField(primary_key=True)
    brand = models.CharField(max_length=100,blank=True, null=True)
    description = models.CharField(max_length=200,blank=True, null=True)
    denomination = models.DecimalField(max_digits=20,decimal_places=2)
    logo = models.ImageField(upload_to='brands/%y%m%d', blank=True, null=True)
    currency = models.CharField(max_length=50, default='SAR')

    class Meta:
        db_table = "dcardbrands"
        verbose_name_plural = "Datacard Brands"

    def image_tag(self):
         return mark_safe('<img src="/media/%s" width="150" height="150" />' % (self.logo))

    def __str__(self):
        return self.brand

class rcardBrands(models.Model):
    id = models.AutoField(primary_key=True)
    brand = models.CharField(max_length=50,blank=True, null=True)
    description = models.CharField(max_length=200,blank=True, null=True)
    denomination = models.DecimalField(max_digits=20,decimal_places=2)
    logo = models.ImageField(upload_to='brands/%y%m%d', blank=True, null=True)
    currency = models.CharField(max_length=50, default='SAR')

    class Meta:
        db_table = "rcardbrands"
        verbose_name_plural = "Rcard Brands"

    def image_tag(self):
         return mark_safe('<img src="/media/%s" width="150" height="150" />' % (self.logo))

    def __str__(self):
        return self.brand

class datacardproducts(models.Model):
    id = models.AutoField(primary_key=True)
    brand = models.ForeignKey('dcardBrands',on_delete=models.CASCADE,related_name='dcardproducts_brand_data',blank=True, null=True)
    username = models.CharField(max_length=100,blank=True, unique=True)
    status = models.BooleanField(default=True)
    cdate = models.DateTimeField(default=datetime.now, blank=True)
    suser = models.ForeignKey('UserData',on_delete=models.CASCADE, related_name='dcardsaleduser_data', blank=True, null=True)
    sdate = models.DateTimeField(null=True, blank=True)
    denomination =  models.DecimalField(null=True,max_digits=20,decimal_places=2)
    fileid = models.ForeignKey('dcarduplogs',on_delete=models.CASCADE,blank=True, null=True)
    productstatus = models.IntegerField(blank=True, null=True, default=0)

    class Meta:
        db_table = "datacardproducts"
        verbose_name_plural = "Datacard Products"

class datacardAssignments(models.Model):
    id = models.AutoField(primary_key=True)
    brand = models.ForeignKey('dcardBrands',on_delete=models.CASCADE,related_name='dcardassignment_brand_data',blank=True, null=True)
    assignedto = models.ForeignKey('UserData',on_delete=models.CASCADE, related_name='dcardassignedto_data', blank=True, null=True)
    assignedby = models.ForeignKey('UserData',on_delete=models.CASCADE, related_name='dcardassignedby_data', blank=True, null=True)
    margin = models.DecimalField(null=True,max_digits=20,decimal_places=2)

    class Meta:
        db_table = "datacardassignments"
        verbose_name_plural = "Datacard Assignments Report"

class rcardProducts(models.Model):
    id = models.AutoField(primary_key=True)
    brand = models.ForeignKey('rcardBrands',on_delete=models.CASCADE,related_name='rcardproducts_brand_data',blank=True, null=True)
    username = models.CharField(max_length=100,blank=True, unique=True)
    status = models.BooleanField(default=True)
    cdate = models.DateTimeField(default=datetime.now, blank=True)
    suser = models.ForeignKey('UserData',on_delete=models.CASCADE, related_name='rcardsaleduser_data', blank=True, null=True)
    sdate = models.DateTimeField(null=True, blank=True)
    denomination =  models.DecimalField(null=True,max_digits=20,decimal_places=2)
    fileid = models.ForeignKey('rcarduplogs',on_delete=models.CASCADE,blank=True, null=True)
    productstatus = models.IntegerField(blank=True, null=True, default=0)

    class Meta:
        db_table = "rcardproducts"
        verbose_name_plural = "Rcard Products"

class rcardAssignments(models.Model):
    id = models.AutoField(primary_key=True)
    brand = models.ForeignKey('rcardBrands',on_delete=models.CASCADE,related_name='rcardassignment_brand_data',blank=True, null=True)
    assignedto = models.ForeignKey('UserData',on_delete=models.CASCADE, related_name='rcardassignedto_data', blank=True, null=True)
    assignedby = models.ForeignKey('UserData',on_delete=models.CASCADE, related_name='rcardassignedby_data', blank=True, null=True)
    margin = models.DecimalField(null=True,max_digits=20,decimal_places=2)

    class Meta:
        db_table = "rcardassignments"
        verbose_name_plural = "Rcard Assignments Report"

class vcloudtransactions(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateTimeField(default=datetime.now, blank=True)
    saleduser = models.ForeignKey('UserData',on_delete=models.CASCADE, related_name='vclouduser_data', blank=True, null=True)
    brand = models.CharField(max_length=50,blank=True)
    type = models.CharField(choices=type,max_length=50,blank=True)
    obalance = models.DecimalField(blank=True,null=True,max_digits=20, decimal_places=2, default=Decimal('0.00'))
    cbalance = models.DecimalField(blank=True,null=True,max_digits=20, decimal_places=2, default=Decimal('0.00'))
    brand_id = models.IntegerField(blank=True,null=True)
    product_id = models.CharField(max_length=50000,blank=True,null=True)
    denominations = models.DecimalField(blank=True,null=True,max_digits=20,decimal_places=2)
    quantity = models.DecimalField(blank=True,null=True,max_digits=20,decimal_places=2)
    amount = models.DecimalField(blank=True,null=True,max_digits=20,decimal_places=2)
    margin1 = models.DecimalField(blank=True,null=True,max_digits=20,decimal_places=2,default=Decimal('0.00'))
    margin2 = models.DecimalField(blank=True,null=True,max_digits=20,decimal_places=2,default=Decimal('0.00'))
    margin3 = models.DecimalField(blank=True,null=True,max_digits=20,decimal_places=2,default=Decimal('0.00'))
    margin4 = models.DecimalField(blank=True,null=True,max_digits=20,decimal_places=2,default=Decimal('0.00'))
    rtype = models.CharField(max_length=100,blank=True,null=True)
    sponser1 = models.ForeignKey('UserData',on_delete=models.CASCADE, related_name='vclouduser_data_sponser1', blank=True, null=True)
    sponser2 = models.ForeignKey('UserData',on_delete=models.CASCADE, related_name='vclouduser_data_sponser2', blank=True, null=True)
    sponser3 = models.ForeignKey('UserData',on_delete=models.CASCADE, related_name='vclouduser_data_sponser3', blank=True, null=True)
    sponser4 = models.ForeignKey('UserData',on_delete=models.CASCADE, related_name='vclouduser_data_sponser4', blank=True, null=True)

    class Meta:
        db_table ="vcloudtransactions"
        verbose_name_plural = "Transaction Report"

class vclouduplogs(models.Model):
    id = models.AutoField(primary_key=True)
    brand = models.ForeignKey('vcloudBrands',on_delete=models.CASCADE, related_name='vcloud_brand_logdata', blank=True, null=True)
    cdate = models.DateTimeField(default=datetime.now, blank=True)
    user = models.ForeignKey('UserData',on_delete=models.CASCADE, related_name='vcloud_uplog_data', blank=True, null=True)
    file = models.FileField(upload_to='csvfiles/%y%m%d', blank=True, null=True)
    pcount = models.IntegerField(blank=True, null=True)
    scount = models.IntegerField(blank=True, null=True)
    status = models.BooleanField(default=True)
    sdate = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table="vclouduplogs"
        verbose_name_plural = "Vcloud Csv Uploaded History"

    def __str__(self):
        return str(self.id)

class vcloudupproducts(models.Model):
    id = models.AutoField(primary_key=True)
    fileid = models.ForeignKey('vclouduplogs',on_delete=models.CASCADE, related_name='vcloud_file_data', blank=True, null=True)
    brand = models.ForeignKey('vcloudBrands',on_delete=models.CASCADE, related_name='vcloud_brand_data', blank=True, null=True)
    denomination = models.DecimalField(blank=True,null=True,max_digits=20,decimal_places=2)
    username = models.CharField(max_length=100,blank=True, unique=True)
    password = models.CharField(max_length=100,blank=True)
    status = models.BooleanField(default=True)

    class Meta:
        db_table="vcloudupproducts"
        verbose_name_plural = "Vcloud Csv Products History"

class SaleSummary(vcloudtransactions):
    class Meta:
        proxy = True
        verbose_name = 'Sale Summary'
        verbose_name_plural = 'Sales Summary'

class dcarduplogs(models.Model):
    id = models.AutoField(primary_key=True)
    brand = models.ForeignKey('dcardBrands',on_delete=models.CASCADE, related_name='dcard_brand_logdata', blank=True, null=True)
    cdate = models.DateTimeField(default=datetime.now, blank=True)
    user = models.ForeignKey('UserData',on_delete=models.CASCADE, related_name='dcard_uplog_data', blank=True, null=True)
    file = models.FileField(upload_to='csvfiles/%y%m%d', blank=True, null=True)
    pcount = models.IntegerField(blank=True, null=True)
    scount = models.IntegerField(blank=True, null=True)
    status = models.BooleanField(default=True)
    sdate = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table="dcarduplogs"
        verbose_name_plural = "Datacard Csv Uploaded History"

    def __str__(self):
        return str(self.id)

class dcardupproducts(models.Model):
    id = models.AutoField(primary_key=True)
    fileid = models.ForeignKey('dcarduplogs',on_delete=models.CASCADE, related_name='dcard_file_data', blank=True, null=True)
    brand = models.ForeignKey('dcardBrands',on_delete=models.CASCADE, related_name='dcard_brand_data', blank=True, null=True)
    denomination = models.DecimalField(blank=True,null=True,max_digits=20,decimal_places=2)
    username = models.CharField(max_length=100,blank=True, unique=True)
    status = models.BooleanField(default=True)

    class Meta:
        db_table="dcardupproducts"
        verbose_name_plural = "Datacard Csv Products History"

class rcarduplogs(models.Model):
    id = models.AutoField(primary_key=True)
    brand = models.ForeignKey('rcardBrands',on_delete=models.CASCADE, related_name='rcard_brand_logdata', blank=True, null=True)
    cdate = models.DateTimeField(default=datetime.now, blank=True)
    user = models.ForeignKey('UserData',on_delete=models.CASCADE, related_name='rcard_uplog_data', blank=True, null=True)
    file = models.FileField(upload_to='csvfiles/%y%m%d', blank=True, null=True)
    pcount = models.IntegerField(blank=True, null=True)
    scount = models.IntegerField(blank=True, null=True)
    status = models.BooleanField(default=True)
    sdate = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table="rcarduplogs"
        verbose_name_plural = "Rcard Csv Uploaded History"

    def __str__(self):
        return str(self.id)

class rcardupproducts(models.Model):
    id = models.AutoField(primary_key=True)
    fileid = models.ForeignKey('rcarduplogs',on_delete=models.CASCADE, related_name='vcloud_file_data', blank=True, null=True)
    brand = models.ForeignKey('rcardBrands',on_delete=models.CASCADE, related_name='vcloud_brand_data', blank=True, null=True)
    denomination = models.DecimalField(blank=True,null=True,max_digits=20,decimal_places=2)
    username = models.CharField(max_length=100,blank=True, unique=True)
    status = models.BooleanField(default=True)

    class Meta:
        db_table="rcardupproducts"
        verbose_name_plural = "Rcard Csv Product History"

class adverisements(models.Model):
    id = models.AutoField(primary_key=True)
    usertype = models.CharField(max_length=50,default='User')
    ctype = models.CharField(max_length=50,default='Vcloud')
    adtype = models.CharField(max_length=50,default='Image')
    adimage = models.ImageField(upload_to='ads/%y%m%d', blank=True, null=True)
    adtext = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        db_table = "adverisements"
        verbose_name_plural = "Advertisements"

    def __str__(self):
        return str(self.usertype)

    def image_tag(self):
         return mark_safe('<img src="/media/%s" width="150" height="150" />' % (self.adimage))

class PurchaseLog(models.Model):
    id = models.AutoField(primary_key=True)
    date = models.DateTimeField(default=datetime.now, blank=True)
    logdesc = models.TextField(max_length=10000,default='User')

    class Meta:
        db_table = "purchaselog"
        verbose_name_plural = "PurchaseLog"
