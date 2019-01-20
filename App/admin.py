from django.contrib import admin
from App.models import *
from django.db.models import Sum, Count

#Register your models here.

class userDataAdmin(admin.ModelAdmin):
    list_display = ('name', 'username', 'email', 'postId', 'sponserId','targetAmt', 'balance')
    list_filter = ('postId', 'sponserId')
    search_fields = ('name','username','sponserId__username')
    change_list_template = 'change_list_graph.html'

class balancetransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'source', 'destination', 'amount','remarks','status')
    list_filter = ('source', 'destination')
    search_fields = ('source__name','destination__name')

class fundTransactionAdmin(admin.ModelAdmin):
    list_display = ('date','source','destination','role','amount','balance')
    list_filter = ('date', 'destination')
    search_fields = ('source__name','destination__name')

class vcloudBrandsAdmin(admin.ModelAdmin):
    list_display = ('id','brand','denomination','category','description','image_tag')
    list_filter = ('category',)
    search_fields = ('brand','category')

class vcloudproductsAdmin(admin.ModelAdmin):
    list_display = ('id','brand','cdate','username','password','suser','sdate','fileid','status')
    list_filter = ('brand', 'status')
    search_fields = ('username',)

class vcloudassignmentsAdmin(admin.ModelAdmin):
    list_display = ('id','brand','assignedto','assignedby','margin')
    list_filter = ('brand', 'assignedto' ,'assignedby')
    search_fields = ('brand__brand','assignedto__name','assignedby__name')

class dcardBrandsAdmin(admin.ModelAdmin):
    list_display = ('id','brand','denomination','description','image_tag')
    search_fields = ('brand',)

class rcardBrandsAdmin(admin.ModelAdmin):
    list_display = ('id','brand','denomination','description','image_tag')
    search_fields = ('brand',)

class rcardproductsAdmin(admin.ModelAdmin):
    list_display = ('id','brand','cdate','username','suser','sdate','status')
    list_filter = ('brand', 'status')
    search_fields = ('username',)

class datacardassignmentsAdmin(admin.ModelAdmin):
    list_display = ('id','brand','assignedto','assignedby','margin')
    list_filter = ('brand', 'assignedto' ,'assignedby')
    search_fields = ('brand__brand','assignedto__name','assignedby__name')

class rcardassignmentsAdmin(admin.ModelAdmin):
    list_display = ('id','brand','assignedto','assignedby','margin')
    list_filter = ('brand', 'assignedto','assignedby')
    search_fields = ('brand__brand','assignedto__name','assignedby__name')

class transactionsAdmin(admin.ModelAdmin):
    list_display = ('id','brand','date','saleduser','type','product_id','denominations','rtype','quantity','amount','sponser1','sponser2','sponser3','sponser4')
    list_filter = ('date','brand', 'saleduser','type','rtype')
    search_fields = ('saleduser__name','brand')
    date_hierarchy = 'date'
    change_list_template = 'change_transaction_list_graph.html'

class datacardproductsAdmin(admin.ModelAdmin):
    list_display = ('id','brand','cdate','username','suser','sdate','status')
    list_filter = ('brand', 'status')
    search_fields = ('username',)

class vclouduplogsAdmin(admin.ModelAdmin):
    list_display = ('id','brand','cdate','user','file','pcount','scount','sdate','status')
    list_filter = ('brand', 'status')
    search_fields = ('brand__brand','username')

class vcloudupproductsAdmin(admin.ModelAdmin):
    list_display = ('id','brand','fileid','username','password','denomination','status')
    list_filter = ('brand', 'status')
    search_fields = ('brand__brand','username')

class dcarduplogsAdmin(admin.ModelAdmin):
    list_display = ('id','brand','cdate','user','file','pcount','scount','sdate','status')
    list_filter = ('brand', 'status')
    search_fields = ('brand__brand','username')

class dcardupproductsAdmin(admin.ModelAdmin):
    list_display = ('id','brand','fileid','username','denomination','status')
    list_filter = ('brand', 'status')
    search_fields = ('brand__brand','username')

class rcarduplogsAdmin(admin.ModelAdmin):
    list_display = ('id','brand','cdate','user','file','pcount','scount','sdate','status')
    list_filter = ('brand', 'status')
    search_fields = ('brand__brand','username')

class rcardupproductsAdmin(admin.ModelAdmin):
    list_display = ('id','brand','fileid','username','denomination','status')
    list_filter = ('brand', 'status')
    search_fields = ('brand__brand','username')

class adsAdmin(admin.ModelAdmin):
    list_display = ('id','usertype','ctype','adtype','adtext','adimage')
    list_filter = ('usertype', 'ctype')
    search_fields = ('adtype','adtext')

class PurchaseLogAdmin(admin.ModelAdmin):
    list_display = ('id','date','logdesc')
    list_filter = ('date',)

class SaleSummaryAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        results=vcloudtransactions.objects.values('type').order_by('type').annotate(totalsales=Sum('amount')).values('type', 'totalsales')

admin.site.register(SaleSummary, SaleSummaryAdmin)
admin.site.register(UserData, userDataAdmin)
admin.site.register(adverisements, adsAdmin)
admin.site.register(balanceTransactionReport, balancetransactionAdmin)
admin.site.register(fundTransactionReport, fundTransactionAdmin)
admin.site.register(vcloudBrands, vcloudBrandsAdmin)
admin.site.register(vcloudProducts, vcloudproductsAdmin)
admin.site.register(vcloudAssignments, vcloudassignmentsAdmin)
admin.site.register(dcardBrands, dcardBrandsAdmin)
admin.site.register(rcardBrands, rcardBrandsAdmin)
admin.site.register(rcardProducts, rcardproductsAdmin)
admin.site.register(rcardAssignments, rcardassignmentsAdmin)
admin.site.register(datacardAssignments, datacardassignmentsAdmin)
admin.site.register(datacardproducts, datacardproductsAdmin)
admin.site.register(vcloudtransactions, transactionsAdmin)
admin.site.register(vclouduplogs, vclouduplogsAdmin)
admin.site.register(vcloudupproducts, vcloudupproductsAdmin)
admin.site.register(dcarduplogs, dcarduplogsAdmin)
admin.site.register(dcardupproducts, dcardupproductsAdmin)
admin.site.register(rcarduplogs, rcarduplogsAdmin)
admin.site.register(rcardupproducts, rcardupproductsAdmin)
admin.site.register(PurchaseLog, PurchaseLogAdmin)
