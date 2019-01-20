"""Project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from App import views
from . import settings
from django.contrib.staticfiles.urls import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.documentation import include_docs_urls
from rest_framework import routers, serializers, viewsets

from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='VoipGulf Api')

from django.conf.urls import (
handler400, handler403, handler404, handler500
)


handler400 = 'App.views.ServerError'
handler404 = 'App.views.PageNotFound'
handler500 = 'App.views.ServerError'


admin.site.site_header = "VoipGulf Console";
admin.site.site_title = "VoipGulf";
admin.site.index_title = "VoipGulf Database";

#router = routers.DefaultRouter()
#router.register('users', UserViewSet)

admin.autodiscover()

urlpatterns = [
    #path('jet/', include('jet.urls','jet')),
    #path('jet/dashboard', include('jet.dashboard.urls','jet-dashboard')),
    path('superadmin/', admin.site.urls, name="admin"),
    path('', views.LoginPage,name="loginPage"),
    path('loginsuccess',views.LoginSubmit, name="loginAction"),
    path('logout',views.logoutclick, name="logout"),
    path('dbfix',views.databasefix, name="databasefix"),

    path('vcloud/home',views.vcloudhomePage, name="homePage"),
    path('vcloud/addReseller',views.vcloudaddReseller, name="addReseller"),
    path('vcloud/newReseller',views.vcloudnewReseller, name="submitReseller"),
    path('vcloud/reseller',views.vcloudviewReseller,name="viewReseller"),
    path('vcloud/addUser',views.vcloudaddUser, name="addUser"),
    path('vcloud/newUser',views.vcloudnewUser, name="submitUser"),
    path('vcloud/user',views.vcloudviewUser,name="viewUser"),
    path('vcloud/profile',views.vcloudprofile,name="profile"),
    path('vcloud/resellerSubmit',views.vcloudeditProfile,name="editProfile"),
    path('vcloud/balanceTransfer',views.vcloudbalanceTransfer,name="balanceTransfer"),
    path('vcloud/addPayment/', views.vcloudaddPayment, name='addPayment'),
    path('vcloud/submit-payment/', views.vcloudsubmitPayment, name='subPayTrans'),
    path('vcloud/btReport', views.vcloudbalanceTransferReport, name='bTReport'),
    path('vcloud/paymentReport', views.vcloudpaymentReport, name='paymentReport'),
    path('vcloud/addvcloudBrand', views.addVcloudBrand, name='addvcloudbrand'),
    path('vcloud/dashboard', views.adminVcloudDashboard, name='vcloudDashboard'),
    path('vcloud/submitVcloudBrands', views.submitVcloudBrands, name='submitVcloudBrands'),
    path('vcloud/manageVcloudBrands', views.manageVcloudBrands, name='manageVcloudBrands'),
    path('vcloud/assignVcloudBrands', views.assignVcloudBrands, name='assignVcloudBrands'),
    path('vcloud/addVcloudProduct', views.addVcloudProduct, name='addVcloudProduct'),
    path('vcloud/submitVcloudProducts', views.submitVcloudProducts, name='submitVcloudProducts'),
    path('ajax/get_vcloud_brand_details/', views.getBrandDetails, name='getBrandDetails'),

    path('ajax/get_vcloud_product_details/', views.getProductDetails, name='getProductDetails'),
    path('ajax/get_datacard_product_details/', views.getDatacardProductDetails, name='getDatacardProductDetails'),
    path('ajax/get_rcard_product_details/', views.getRcardProductDetails, name='getRcardProductDetails'),

    path('dcard/editsubmitproduct/', views.editsubmitManagedcardProducts, name='editsubmitManagedcardProducts'),
    path('rcard/editsubmitproduct/', views.editsubmitManagercardProducts, name='editsubmitManagercardProducts'),

    path('vcloud/managebrands/', views.submitManageBrands, name='submitManageBrands'),
    path('vcloud/store', views.vcloudStore, name='vcloudStore'),
    path('vcloud/manage_products/', views.vcloudmanageProduct, name='vcloudmanageProduct'),
    path('vcloud/editsubmitproduct/', views.editsubmitManageProducts, name='editsubmitManageProducts'),
    path('vcloud/vcloud-report/', views.vcloudreport, name='vcloudreport'),
    path('vcloud/store/filter/<str:brandtype>', views.filteredvcloudstore,name='filteredvcloudstore'),
    path('ajax/assign_vcloud_brands/', views.saveassignVcloudBrands, name='saveassignVcloudBrands'),
    path('vcloud/submit-balance-transfer/', views.vcloudSubmitBalanceTransfer, name='subBalTrans'),
    path('printLayout', views.printLayout, name='printlayout'),

    path('ajax/validate_username/', views.validate_username, name='validate_username'),
    path('ajax/get_brandlist/', views.getBrandWithTypes, name='getBrandWithTypes'),
    path('ajax/get_user_or_reseller/', views.getReseller_UserList, name='getuserlist'),
    path('ajax/get_user_or_reseller_credit/', views.getCreditBalance, name='getCredit'),
    path('ajax/edit-reseller-view/', views.vcloudeditResellerView, name='editReseller'),
    path('ajax/edit-reseller-edit/', views.editReseller, name='editReseller'),
    path('editReseller/', views.submitEditUsers, name='submitEditUsers'),

    path('dcard/dashboard', views.adminDcardDashboard, name='adminDcardDashboard'),
    path('dcard/addReseller', views.dcardaddReseller, name='addResellerDcard'),
    path('dcard/addUser', views.dcardaddUser, name='addUserDcard'),
    path('dcard/newReseller',views.dcardnewReseller, name="dcardsubmitReseller"),
    path('dcard/reseller',views.dcardviewReseller,name="viewResellerDcard"),
    path('dcard/newUser',views.dcardnewUser, name="dcardsubmitUser"),
    path('dcard/user',views.dcardviewUser,name="viewUserDcard"),
    path('dcard/profile',views.dcardprofile,name="profiledcard"),
    path('dcard/resellerSubmit',views.dcardeditProfile,name="editProfileDcard"),
    path('dcard/balanceTransfer',views.dcardbalanceTransfer,name="balanceTransferDcard"),
    path('dcard/submit-balance-transfer/', views.dcardSubmitBalanceTransfer, name='subBalTransDcard'),
    path('dcard/addPayment/', views.dcardaddPayment, name='addPaymentDcard'),
    path('dcard/submit-payment/', views.dcardsubmitPayment, name='subPayTransDcard'),
    path('dcard/btReport', views.dcardbalanceTransferReport, name='bTReportDcard'),
    path('dcard/paymentReport', views.dcardpaymentReport, name='paymentReportDcard'),
    path('dcard/addDCardBrand', views.addDCardBrand, name='addDCardbrand'),
    path('dcard/submitDCardBrands', views.submitDCardBrands, name='submitDCardBrands'),
    path('dcard/manageDCardBrands', views.manageDCardBrands, name='manageDCardBrands'),
    path('dcard/assignDCardBrands', views.assignDCardBrands, name='assignDCardBrands'),
    path('ajax/get_dcard_brand_details/', views.getDCardBrandDetails, name='getDCardBrandDetails'),
    path('dcard/submitDcardManageBrands/', views.submitDcardManageBrands, name='submitDcardManageBrands'),
    path('dcard/addDCardProduct', views.adddcardProduct, name='adddcardProduct'),
    path('dcard/submitdcardProducts', views.submitdcardProducts, name='submitdcardProducts'),
    path('dcard/manage_products/', views.dcardmanageProduct, name='dcardmanageProduct'),
    path('ajax/assign_dcard_brands/', views.saveassignDCardBrands, name='saveassignDCardBrands'),
    path('dcard/store/', views.dcardstore, name='dcardstore'),
    path('dcard/store/filter/<str:brand>', views.filtereddatastore,name='filtereddatastore'),
    path('dcard/dcard-report/', views.datacardreport, name='datacardreport'),

    path('rcard/dashboard', views.adminRcardDashboard, name='adminRcardDashboard'),
    path('rcard/addReseller', views.rcardaddReseller, name='addResellerRcard'),
    path('rcard/addUser', views.rcardaddUser, name='addUserRcard'),
    path('rcard/newReseller',views.rcardnewReseller, name="RcardsubmitReseller"),
    path('rcard/reseller',views.rcardviewReseller,name="viewResellerRcard"),
    path('rcard/newUser',views.rcardnewUser, name="RcardsubmitUser"),
    path('rcard/user',views.rcardviewUser,name="viewUserRcard"),
    path('rcard/profile',views.rcardprofile,name="profileRcard"),
    path('rcard/resellerSubmit',views.rcardeditProfile,name="editProfileRcard"),
    path('rcard/balanceTransfer',views.rcardbalanceTransfer,name="balanceTransferRcard"),
    path('rcard/submit-balance-transfer/', views.rcardSubmitBalanceTransfer, name='subBalTransRcard'),
    path('rcard/addPayment/', views.rcardaddPayment, name='addPaymentRcard'),
    path('rcard/submit-payment/', views.rcardsubmitPayment, name='subPayTransRcard'),
    path('rcard/btReport', views.rcardbalanceTransferReport, name='bTReportRcard'),
    path('rcard/paymentReport', views.rcardpaymentReport, name='paymentReportRcard'),
    path('rcard/addRCardBrand', views.addRCardBrand, name='addRCardbrand'),
    path('rcard/submitRCardBrands', views.submitRCardBrands, name='submitRCardBrands'),
    path('rcard/manageRCardBrands', views.manageRCardBrands, name='manageRCardBrands'),
    path('rcard/assignRCardBrands', views.assignRCardBrands, name='assignRCardBrands'),
    path('rcard/addRCardProduct', views.addrcardProduct, name='addrcardProduct'),
    path('rcard/submitrcardProducts', views.submitrcardProducts, name='submitrcardProducts'),
    path('rcard/manage_products/', views.rcardmanageProduct, name='rcardmanageProduct'),
    path('ajax/assign_rcard_brands/', views.saveassignRCardBrands, name='saveassignRCardBrands'),
    path('rcard/store/', views.rcardstore, name='rcardstore'),
    path('rcard/store/filter/<str:brand>', views.filteredrcardstore,name='filteredrcardstore'),
    path('rcard/rcard-report/', views.rcardreport, name='rcardreport'),
    path('ajax/get_rcard_brand_details/', views.getRCardBrandDetails, name='getRCardBrandDetails'),
    path('rcard/submitRcardManageBrands/', views.submitRcardManageBrands, name='submitrcardManageBrands'),

    path('reseller/vcloud/home/', views.resellervcloudhomePage, name='resellervcloudhomePage'),
    path('reseller/vcloud/profile/', views.resellervcloudprofile, name='resellervcloudprofile'),
    path('reseller/vcloud/addReseller', views.resellervcloudaddReseller, name="reselleraddReseller"),
    path('reseller/vcloud/newReseller', views.resellervcloudnewReseller, name="resellersubmitReseller"),
    path('reseller/vcloud/reseller', views.resellervcloudviewReseller,name="resellerviewReseller"),
    path('reseller/vcloud/addUser', views.resellervcloudaddUser, name="reselleraddUser"),
    path('reseller/vcloud/newUser', views.resellervcloudnewUser, name="resellersubmitUser"),
    path('reseller/vcloud/user', views.resellervcloudviewUser, name="resellerviewUser"),
    path('reseller/vcloud/resellerSubmit',views.resellervcloudeditProfile, name="resellereditProfile"),
    path('reseller/vcloud/balanceTransfer',views.resellervcloudbalanceTransfer, name="resellerbalanceTransfer"),
    path('reseller/vcloud/addPayment/', views.resellervcloudaddPayment, name='reselleraddPayment'),
    path('reseller/vcloud/submit-payment/', views.resellervcloudsubmitPayment, name='resellersubPayTrans'),
    path('reseller/vcloud/btReport', views.resellervcloudbalanceTransferReport, name='resellerbTReport'),
    path('reseller/vcloud/paymentReport', views.resellervcloudpaymentReport, name='resellerpaymentReport'),
    path('reseller/vcloud/vcloud-report/', views.resellervcloudreport, name='resellervcloudreport'),
    path('reseller/vcloud/store', views.resellervcloudStore, name='resellervcloudStore'),
    path('reseller/vcloud/viewbrands', views.resellerviewbrands, name='resellerviewbrands'),
    path('reseller/vcloud/assignVcloudBrands', views.resellerassignVcloudBrands, name='resellerassignVcloudBrands'),
    path('reseller/vcloud/store/filter/<str:brandtype>', views.resellerfilteredvcloudstore,name='resellerfilteredvcloudstore'),
    path('reseller/vcloud/submit-balance-transfer/', views.resellervcloudSubmitBalanceTransfer, name='resellersubBalTrans'),
    path('ajax/buy_vcloud_brands/', views.buy_vcloud_brands, name='buy_vcloud_brands'),

    path('reseller/dcard/dashboard', views.resellerDcardDashboard, name='resellerDcardDashboard'),
    path('reseller/dcard/profile',views.resellerprofiledcard,name="resellerprofiledcard"),
    path('reseller/dcard/addReseller', views.reselleraddResellerDcard, name='reselleraddResellerDcard'),
    path('reseller/dcard/addUser', views.reselleraddUserDcard, name='reselleraddUserDcard'),
    path('reseller/dcard/viewReseller', views.resellerviewResellerDcard, name='resellerviewResellerDcard'),
    path('reseller/dcard/viewUser', views.resellerviewUserDcard, name='resellerviewUserDcard'),
    path('reseller/dcard/balancetransfer', views.resellerbalanceTransferDcard, name='resellerbalanceTransferDcard'),
    path('reseller/dcard/addPayment', views.reselleraddPaymentDcard, name='reselleraddPaymentDcard'),
    path('reseller/dcard/vcloudreport', views.resellerdatacardreport, name='resellerdatacardreport'),
    path('reseller/dcard/btReport', views.resellerbTReportDcard, name='resellerbTReportDcard'),
    path('reseller/dcard/paymentReport', views.resellerpaymentReportDcard, name='resellerpaymentReportDcard'),
    path('reseller/dcard/assignBrand', views.resellerassignDCardBrands, name='resellerassignDCardBrands'),
    path('reseller/dcard/store', views.resellerdcardstore, name='resellerdcardstore'),
    path('reseller/dcard/editProfile', views.editresellerProfileDcard, name='editresellerProfileDcard'),
    path('reseller/dcard/submitReseller', views.resellerdcardsubmitReseller, name='resellerdcardsubmitReseller'),
    path('reseller/dcard/submitUser', views.resellersubmitUser, name='resellersubmitUser'),
    path('reseller/dcard/reseller-submit-balance-transfer', views.resellersubBalTransDcard, name='resellersubBalTransDcard'),
    path('reseller/dcard/submit-payment', views.resellerdcardsubPayTrans, name='resellerdcardsubPayTrans'),
    path('reseller/dcard/viewbrands',views.resellerdcardviewbrands, name='resellerdcardviewbrands'),
    path('reseller/dcard/store/filter/<str:brand>', views.resellerfilterdcardstore,name='resellerfilterdcardstore'),
    path('ajax/buy_datacard_brands/', views.buy_datacard_brands, name='buy_datacard_brands'),

    path('reseller/rcard/dashboard', views.resellerRcardDashboard, name='resellerRcardDashboard'),
    path('reseller/rcard/profile',views.resellerprofilercard,name="resellerprofilercard"),
    path('reseller/rcard/addReseller', views.reselleraddResellerRcard, name='reselleraddResellerRcard'),
    path('reseller/rcard/addUser', views.reselleraddUserRcard, name='reselleraddUserRcard'),
    path('reseller/rcard/viewReseller', views.resellerviewResellerRcard, name='resellerviewResellerRcard'),
    path('reseller/rcard/viewUser', views.resellerviewUserRcard, name='resellerviewUserRcard'),
    path('reseller/rcard/balancetransfer', views.resellerbalanceTransferRcard, name='resellerbalanceTransferRcard'),
    path('reseller/rcard/addPayment', views.reselleraddPaymentRcard, name='reselleraddPaymentRcard'),
    path('reseller/rcard/vcloudreport', views.resellerrcardreport, name='resellerrcardreport'),
    path('reseller/rcard/btReport', views.resellerbTReportRcard, name='resellerbTReportRcard'),
    path('reseller/rcard/paymentReport', views.resellerpaymentReportRcard, name='resellerpaymentReportRcard'),
    path('reseller/rcard/assignBrand', views.resellerassignRCardBrands, name='resellerassignRCardBrands'),
    path('reseller/rcard/store', views.resellerrcardstore, name='resellerrcardstore'),
    path('reseller/rcard/editProfile', views.editresellerProfileRcard, name='editresellerProfileRcard'),
    path('reseller/rcard/submitReseller', views.resellerrcardsubmitReseller, name='resellerrcardsubmitReseller'),
    path('reseller/rcard/submitUser', views.resellerrcardsubmitUser, name='resellerrcardsubmitUser'),
    path('reseller/rcard/reseller-submit-balance-transfer', views.resellersubBalTransRcard, name='resellersubBalTransRcard'),
    path('reseller/rcard/submit-payment', views.resellerrcardsubPayTrans, name='resellerrcardsubPayTrans'),
    path('reseller/rcard/viewbrands',views.resellerrcardviewbrands, name='resellerrcardviewbrands'),
    path('reseller/rcard/store/filter/<str:brand>', views.resellerfilterrcardstore,name='resellerfilterrcardstore'),
    path('ajax/buy_rcard_brands/', views.buy_rcard_brands, name='buy_rcard_brands'),

    path('subreseller/vcloud/home/', views.subresellervcloudhomePage, name='subresellervcloudhomePage'),
    path('subreseller/vcloud/profile/', views.subresellervcloudprofile, name='subresellervcloudprofile'),
    path('subreseller/vcloud/addUser', views.subresellervcloudaddUser, name="subresellervcloudaddUser"),
    path('subreseller/vcloud/newUser', views.subresellervcloudnewUser, name="subresellervcloudnewUser"),
    path('subreseller/vcloud/user', views.subresellervcloudviewUser, name="subresellervcloudviewUser"),
    path('subreseller/vcloud/resellerSubmit',views.subresellervcloudeditProfile, name="subresellervcloudeditProfile"),
    path('subreseller/vcloud/balanceTransfer',views.subresellervcloudbalanceTransfer, name="subresellervcloudbalanceTransfer"),
    path('subreseller/vcloud/addPayment/', views.subresellervcloudaddPayment, name='subresellervcloudaddPayment'),
    path('subreseller/vcloud/submit-payment/', views.subresellervcloudsubmitPayment, name='subresellervcloudsubmitPayment'),
    path('subreseller/vcloud/btReport', views.subresellervcloudbalanceTransferReport, name='subresellervcloudbalanceTransferReport'),
    path('subreseller/vcloud/paymentReport', views.subresellervcloudpaymentReport, name='subresellervcloudpaymentReport'),
    path('subreseller/vcloud/vcloud-report/', views.subresellervcloudreport, name='subresellervcloudreport'),
    path('subreseller/vcloud/store', views.subresellervcloudStore, name='subresellervcloudStore'),
    path('subreseller/vcloud/viewbrands', views.subresellerviewbrands, name='subresellerviewbrands'),
    path('subreseller/vcloud/assignVcloudBrands', views.subresellerassignVcloudBrands, name='subresellerassignVcloudBrands'),
    path('subreseller/vcloud/store/filter/<str:brandtype>', views.subresellerfilteredvcloudstore,name='subresellerfilteredvcloudstore'),
    path('subreseller/vcloud/submit-balance-transfer/', views.subresellervcloudSubmitBalanceTransfer, name='subresellervcloudSubmitBalanceTransfer'),
    path('ajax/sub_buy_vcloud_brands/', views.sub_buy_vcloud_brands, name='sub_buy_vcloud_brands'),

    path('subreseller/dcard/dashboard', views.subresellerDcardDashboard, name='subresellerDcardDashboard'),
    path('subreseller/dcard/profile',views.subresellerprofiledcard,name="subresellerprofiledcard"),
    path('subreseller/dcard/addUser', views.subreselleraddUserDcard, name='subreselleraddUserDcard'),
    path('subreseller/dcard/viewUser', views.subresellerviewUserDcard, name='subresellerviewUserDcard'),
    path('subreseller/dcard/balancetransfer', views.subresellerbalanceTransferDcard, name='subresellerbalanceTransferDcard'),
    path('subreseller/dcard/addPayment', views.subreselleraddPaymentDcard, name='subreselleraddPaymentDcard'),
    path('subreseller/dcard/vcloudreport', views.subresellerdatacardreport, name='subresellerdatacardreport'),
    path('subreseller/dcard/btReport', views.subresellerbTReportDcard, name='subresellerbTReportDcard'),
    path('subreseller/dcard/paymentReport', views.subresellerpaymentReportDcard, name='subresellerpaymentReportDcard'),
    path('subreseller/dcard/assignBrand', views.subresellerassignDCardBrands, name='subresellerassignDCardBrands'),
    path('subreseller/dcard/store', views.subresellerdcardstore, name='subresellerdcardstore'),
    path('subreseller/dcard/editProfile', views.subeditresellerProfileDcard, name='subeditresellerProfileDcard'),
    path('subreseller/dcard/submitUser', views.subresellersubmitUser, name='subresellersubmitUser'),
    path('subreseller/dcard/reseller-submit-balance-transfer', views.subresellersubBalTransDcard, name='subresellersubBalTransDcard'),
    path('subreseller/dcard/submit-payment', views.subresellersubPayTrans, name='subresellersubPayTrans'),
    path('subreseller/dcard/viewbrands',views.subresellerdcardviewbrands, name='subresellerdcardviewbrands'),
    path('subreseller/dcard/store/filter/<str:brand>', views.subresellerfilterdcardstore,name='subresellerfilterdcardstore'),
    path('ajax/sub_buy_datacard_brands/', views.sub_buy_datacard_brands, name='sub_buy_datacard_brands'),

    path('subreseller/rcard/dashboard', views.subresellerRcardDashboard, name='subresellerRcardDashboard'),
    path('subreseller/rcard/profile',views.subresellerprofilercard,name="subresellerprofilercard"),
    path('subreseller/rcard/addUser', views.subreselleraddUserRcard, name='subreselleraddUserRcard'),
    path('subreseller/rcard/viewUser', views.subresellerviewUserRcard, name='subresellerviewUserRcard'),
    path('subreseller/rcard/balancetransfer', views.subresellerbalanceTransferRcard, name='subresellerbalanceTransferRcard'),
    path('subreseller/rcard/addPayment', views.subreselleraddPaymentRcard, name='subreselleraddPaymentRcard'),
    path('subreseller/rcard/vcloudreport', views.subresellerrcardreport, name='subresellerrcardreport'),
    path('subreseller/rcard/btReport', views.subresellerbTReportRcard, name='subresellerbTReportRcard'),
    path('subreseller/rcard/paymentReport', views.subresellerpaymentReportRcard, name='subresellerpaymentReportRcard'),
    path('subreseller/rcard/assignBrand', views.subresellerassignRCardBrands, name='subresellerassignRCardBrands'),
    path('subreseller/rcard/store', views.subresellerrcardstore, name='subresellerrcardstore'),
    path('subreseller/rcard/editProfile', views.subeditresellerProfileRcard, name='subeditresellerProfileRcard'),
    path('subreseller/rcard/submitUser', views.subresellersubmitUser, name='subresellersubmitUser'),
    path('subreseller/rcard/reseller-submit-balance-transfer', views.subresellersubBalTransRcard, name='subresellersubBalTransRcard'),
    path('subreseller/rcard/submit-payment', views.subresellerrcardsubPayTrans, name='subresellerrcardsubPayTrans'),
    path('subreseller/rcard/viewbrands',views.subresellerrcardviewbrands, name='subresellerrcardviewbrands'),
    path('subreseller/rcard/store/filter/<str:brand>', views.subresellerfilterrcardstore,name='subresellerfilterrcardstore'),
    path('ajax/sub_buy_rcard_brands/', views.sub_buy_rcard_brands, name='sub_buy_rcard_brands'),

    path('user/vcloud/home/', views.uservcloudhomePage, name='uservcloudhomePage'),
    path('user/vcloud/profile/', views.uservcloudprofile, name='uservcloudprofile'),
    path('user/vcloud/vcloud-report/', views.userrvcloudreport, name='uservcloudreport'),
    path('user/vcloud/store', views.uservcloudStore, name='uservcloudStore'),
    path('user/vcloud/store/filter/<str:brandtype>', views.userfilteredvcloudstore,name='userfilteredvcloudstore'),
    path('user/vcloud/viewbrands', views.userviewbrands, name='userviewbrands'),
    path('user/vcloud/resellerSubmit',views.uservcloudeditProfile, name="usereditProfile"),
    path('ajax/user_buy_vcloud_brands/', views.user_buy_vcloud_brands, name='user_buy_vcloud_brands'),

    path('user/dcard/home/', views.userDcardDashboard, name='userDcardDashboard'),
    path('user/dcard/profile/', views.userprofiledcard, name='userprofiledcard'),
    path('user/dcard/vcloud-report/', views.userdatacardreport, name='userdatacardreport'),
    path('user/dcard/store', views.userdcardstore, name='userdcardstore'),
    path('user/dcard/store/filter/<str:brandtype>', views.userfilterdcardstore,name='userfilterdcardstore'),
    path('user/dcard/viewbrands', views.userdcardviewbrands, name='userdcardviewbrands'),
    path('user/dcard/resellerSubmit',views.usereditProfileDcard, name="usereditProfileDcard"),
    path('ajax/user_buy_dcard_brands/', views.user_buy_datacard_brands, name='user_buy_datacard_brands'),

    path('user/rcard/home/', views.userRcardDashboard, name='userRcardDashboard'),
    path('user/rcard/profile/', views.userprofileRcard, name='userprofileRcard'),
    path('user/rcard/vcloud-report/', views.userrcardreport, name='userrcardreport'),
    path('user/rcard/store', views.userrcardstore, name='userrcardstore'),
    path('user/rcard/store/filter/<str:brand>', views.userfilterrcardstore,name='userfilterrcardstore'),
    path('user/rcard/viewbrands', views.userrcardviewbrands, name='userrcardviewbrands'),
    path('user/rcard/resellerSubmit',views.usereditProfilercard, name="usereditProfilercard"),
    path('ajax/user_buy_rcard_brands/', views.user_buy_rcard_brands, name='user_buy_rcard_brands'),

    #________________Need To Update On Hosted SIte_______________
    path('vcloud/addcsvProduct',views.addcsvProduct, name='addcsvProduct'),
    path('vcloud/submitcsvProduct',views.vcloudcsvupload, name='vcloudcsvupload'),
    path('vcloud/log/to/prdct/<int:id>',views.vcloudlogtoproduct, name='vcloudlogtoproduct'),
    path('vcloud/log/to/prdctdelete/<int:id>',views.vcloudlogtoproductdelete, name='vcloudlogtoproductdelete'),

    path('dcard/addcsvProduct',views.adddcardcsvProduct, name='adddcardcsvProduct'),
    path('dcard/submitcsvProduct',views.dcardcsvupload, name='dcardcsvupload'),
    path('dcard/log/to/prdct/<int:id>',views.dcardlogtoproduct, name='dcardlogtoproduct'),
    path('dcard/log/to/prdctdelete/<int:id>',views.dcardlogtoproductdelete, name='dcardlogtoproductdelete'),

    path('rcard/addcsvProduct',views.addrcardcsvProduct, name='addrcardcsvProduct'),
    path('rcard/submitcsvProduct',views.rcardcsvupload, name='rcardcsvupload'),
    path('rcard/log/to/prdct/<int:id>',views.rcardlogtoproduct, name='rcardlogtoproduct'),
    path('rcard/log/to/prdctdelete/<int:id>',views.rcardlogtoproductdelete, name='rcardlogtoproductdelete'),

    path('vcloud/home/filter',views.filtervcloudhomepage, name='filtervcloudhomepage'),
    path('reseller/vcloud/home/filter',views.filterresellervcloudhomepage, name='filterresellervcloudhomepage'),
    path('subreseller/vcloud/home/filter',views.filtersubresellervcloudhomepage, name='filtersubresellervcloudhomepage'),
    path('user/vcloud/home/filter',views.filteruservcloudhomepage, name='filteruservcloudhomepage'),

    path('dcard/home/filter',views.filterdcardhomepage, name='filterdcardhomepage'),
    path('reseller/dcard/home/filter',views.filterresellerDcardDashboard, name='filterresellerDcardDashboard'),
    path('subreseller/dcard/home/filter',views.filtersubresellerDcardDashboard, name='filtersubresellerDcardDashboard'),
    path('user/dcard/home/filter',views.filteruserDcardDashboard, name='filteruserDcardDashboard'),

    path('rcard/home/filter',views.filterrcardhomepage, name='filterrcardhomepage'),
    path('reseller/rcard/home/filter',views.filterresellerrcardhomepage, name='rcardDashboardfilter'),
    path('subreseller/rcard/home/filter',views.filtersubresellerrcardDashboard, name='subresellerrcardDashboardfilter'),
    path('user/rcard/home/filter',views.filteruserrcardDashboard, name='filteruserRcardDashboard'),

    path('ajax/get_product_details/', views.get_product_details,name='get_product_details'),
    path('ajax/get_margin_details/', views.getAllMargin,name='get_margin_details'),

    path('vcloud/vcloud-report/filter', views.filtervcloud_report,name='filtervcloudreport'),
    path('dcard/vcloud-report/filter', views.filterdcard_report,name='filterdcardreport'),
    path('rcard/vcloud-report/filter', views.filterrcard_report,name='filterrcardreport'),

    path('reseller/vcloud/vcloud-report/filter', views.filterresellervcloud_report,name='resellerfiltervcloudreport'),
    path('reseller/dcard/vcloud-report/filter', views.filterresellerdcard_report,name='resellerfilterdcardreport'),
    path('reseller/rcard/vcloud-report/filter', views.filterresellerrcard_report,name='resellerfilterrcardreport'),

    path('subreseller/vcloud/vcloud-report/filter', views.filtersubresellervcloud_report,name='filtersubresellervcloudreport'),
    path('subreseller/dcard/vcloud-report/filter', views.filtersubresellerdcard_report,name='filtersubresellerdcardreport'),
    path('subreseller/rcard/vcloud-report/filter', views.filtersubresellerrcard_report,name='filtersubresellerrcardreport'),

    path('user/vcloud/vcloud-report/filter', views.filteruservcloud_report,name='filteruservcloudreport'),
    path('user/dcard/vcloud-report/filter', views.filteruserdcard_report,name='filteruserdcardreport'),
    path('user/rcard/vcloud-report/filter', views.filteruserrcard_report,name='filteruserrcardreport'),

    path('vcloud/btReport/filter', views.filtervcloudbtreport, name='filtervcloudbTReport'),
    path('dcard/btReport/filter', views.filterdcardbtreport, name='filterdcardbTReport'),
    path('rcard/btReport/filter', views.filterrcardbtreport, name='filterrcardbTReport'),

    path('reseller/vcloud/btReport/filter', views.filterresellervcloudbtreport, name='filterresellervcloudbTReport'),
    path('reseller/dcard/btReport/filter', views.filterresellerdcardbtreport, name='filterresellerdcardbTReport'),
    path('reseller/rcard/btReport/filter', views.filterresellerrcardbtreport, name='filterresellerrcardbTReport'),

    path('subreseller/vcloud/btReport/filter', views.filtersubresellervcloudbtreport, name='filtersubresellervcloudbTReport'),
    path('subreseller/dcard/btReport/filter', views.filtersubresellerdcardbtreport, name='filtersubresellerdcardbTReport'),
    path('subreseller/rcard/btReport/filter', views.filtersubresellerrcardbtreport, name='filtersubresellerrcardbTReport'),

    path('vcloud/paymentReport/filter', views.filtervcloudpaymentreport, name='filtervcloudpaymentreport'),
    path('dcard/paymentReport/filter', views.filterdcardpaymentreport, name='filterdcardpaymentreport'),
    path('rcard/paymentReport/filter', views.filterrcardpaymentreport, name='filterrcardpaymentreport'),

    path('reseller/vcloud/paymentReport/filter', views.filterresellervcloudpaymentreport, name='filterresellervcloudpaymentreport'),
    path('reseller/dcard/paymentReport/filter', views.filterresellerdcardpaymentreport, name='filterresellerdcardpaymentreport'),
    path('reseller/rcard/paymentReport/filter', views.filterresellerrcardpaymentreport, name='filterresellerrcardpaymentreport'),

    path('subreseller/vcloud/paymentReport/filter', views.filtersubresellervcloudpaymentreport, name='filtersubresellervcloudpaymentreport'),
    path('subreseller/dcard/paymentReport/filter', views.filtersubresellerdcardpaymentreport, name='filtersubresellerdcardpaymentreport'),
    path('subreseller/rcard/paymentReport/filter', views.filtersubresellerrcardpaymentreport, name='filtersubresellerrcardpaymentreport'),

    path('vcloud/changepassword',views.vcloudchangepassword, name="vcloudchangepassword"),
    path('vcloud/submitchangepassword',views.submitvcloudchangepassword, name="submitvcloudchangepassword"),
    path('dcard/changepassword',views.dcardchangepassword, name="dcardchangepassword"),
    path('dcard/submitchangepassword',views.submitdcardchangepassword, name="submitdcardchangepassword"),
    path('rcard/changepassword',views.rcardchangepassword, name="rcardchangepassword"),
    path('rcard/submitchangepassword',views.submitrcardchangepassword, name="submitrcardchangepassword"),

    path('reseller/vcloud/changepassword',views.resellervcloudchangepassword, name="resellervcloudchangepassword"),
    path('reseller/vcloud/submitchangepassword',views.resellersubmitvcloudchangepassword, name="resellersubmitvcloudchangepassword"),
    path('reseller/dcard/changepassword',views.resellerdcardchangepassword, name="resellerdcardchangepassword"),
    path('reseller/dcard/submitchangepassword',views.resellersubmitdcardchangepassword, name="resellersubmitdcardchangepassword"),
    path('reseller/rcard/changepassword',views.resellerrcardchangepassword, name="resellerrcardchangepassword"),
    path('reseller/rcard/submitchangepassword',views.resellersubmitrcardchangepassword, name="resellersubmitrcardchangepassword"),

    path('subreseller/vcloud/changepassword',views.subresellervcloudchangepassword, name="subresellervcloudchangepassword"),
    path('subreseller/vcloud/submitchangepassword',views.subresellersubmitvcloudchangepassword, name="subresellersubmitvcloudchangepassword"),
    path('subreseller/dcard/changepassword',views.subresellerdcardchangepassword, name="subresellerdcardchangepassword"),
    path('subreseller/dcard/submitchangepassword',views.subresellersubmitdcardchangepassword, name="subresellersubmitdcardchangepassword"),
    path('subreseller/rcard/changepassword',views.subresellerrcardchangepassword, name="subresellerrcardchangepassword"),
    path('subreseller/rcard/submitchangepassword',views.subresellersubmitrcardchangepassword, name="subresellersubmitrcardchangepassword"),

    path('user/vcloud/changepassword',views.uservcloudchangepassword, name="uservcloudchangepassword"),
    path('user/vcloud/submitchangepassword',views.usersubmitvcloudchangepassword, name="usersubmitvcloudchangepassword"),
    path('user/dcard/changepassword',views.userdcardchangepassword, name="userdcardchangepassword"),
    path('user/dcard/submitchangepassword',views.usersubmitdcardchangepassword, name="usersubmitdcardchangepassword"),
    path('user/rcard/changepassword',views.userrcardchangepassword, name="userrcardchangepassword"),
    path('user/rcard/submitchangepassword',views.usersubmitrcardchangepassword, name="usersubmitrcardchangepassword"),

    path('admin/vcloud/reseller/changestatus/<str:username>', views.vcloudchangeResellerStatus, name='vcloudchangeResellerStatus'),
    path('admin/dcard/reseller/changestatus/<str:username>', views.dcardchangeResellerStatus, name='dcardchangeResellerStatus'),
    path('admin/rcard/reseller/changestatus/<str:username>', views.rcardchangeResellerStatus, name='rcardchangeResellerStatus'),
    path('admin/vcloud/user/changestatus/<str:username>', views.vcloudchangeUserStatus, name='vcloudchangeUserStatus'),
    path('admin/dcard/user/changestatus/<str:username>', views.dcardchangeUserStatus, name='dcardchangeUserStatus'),
    path('admin/rcard/user/changestatus/<str:username>', views.rcardchangeUserStatus, name='rcardchangeUserStatus'),

    path('reseller/vcloud/reseller/changestatus/<str:username>', views.resellervcloudchangeResellerStatus, name='resellervcloudchangeResellerStatus'),
    path('reseller/dcard/reseller/changestatus/<str:username>', views.resellerdcardchangeResellerStatus, name='resellerdcardchangeResellerStatus'),
    path('reseller/rcard/reseller/changestatus/<str:username>', views.resellerrcardchangeResellerStatus, name='resellerrcardchangeResellerStatus'),
    path('reseller/vcloud/user/changestatus/<str:username>', views.resellervcloudchangeUserStatus, name='resellervcloudchangeUserStatus'),
    path('reseller/dcard/user/changestatus/<str:username>', views.resellerdcardchangeUserStatus, name='resellerdcardchangeUserStatus'),
    path('reseller/rcard/user/changestatus/<str:username>', views.resellerrcardchangeUserStatus, name='resellerrcardchangeUserStatus'),

    path('subreseller/vcloud/user/changestatus/<str:username>', views.subresellervcloudchangeUserStatus, name='subresellervcloudchangeUserStatus'),
    path('subreseller/dcard/user/changestatus/<str:username>', views.subresellerdcardchangeUserStatus, name='subresellerdcardchangeUserStatus'),
    path('subreseller/rcard/user/changestatus/<str:username>', views.subresellerrcardchangeUserStatus, name='subresellerrcardchangeUserStatus'),


    path('admin/vcloud/reseller/passwordreset/<str:username>', views.resetpasswordvcloudreseller, name='resetpasswordvcloudreseller'),
    path('admin/vcloud/user/passwordreset/<str:username>', views.resetpasswordvclouduser, name='resetpasswordvclouduser'),
    path('admin/dcard/reseller/passwordreset/<str:username>', views.resetpassworddcardreseller, name='resetpassworddcardreseller'),
    path('admin/dcard/user/passwordreset/<str:username>', views.resetpassworddcarduser, name='resetpassworddcarduser'),
    path('admin/rcard/reseller/passwordreset/<str:username>', views.resetpasswordrcardreseller, name='resetpasswordrcardreseller'),
    path('admin/rcard/user/passwordreset/<str:username>', views.resetpasswordrcarduser, name='resetpasswordrcarduser'),

    path('reseller/vcloud/reseller/passwordreset/<str:username>', views.resetpasswordresellervcloudreseller, name='resetpasswordresellervcloudreseller'),
    path('reseller/vcloud/user/passwordreset/<str:username>', views.resetpasswordresellervclouduser, name='resetpasswordresellervclouduser'),
    path('reseller/dcard/reseller/passwordreset/<str:username>', views.resetpasswordresellerdcardreseller, name='resetpasswordresellerdcardreseller'),
    path('reseller/dcard/user/passwordreset/<str:username>', views.resetpasswordresellerdcarduser, name='resetpasswordresellerdcarduser'),
    path('reseller/rcard/reseller/passwordreset/<str:username>', views.resetpasswordresellerrcardreseller, name='resetpasswordresellerrcardreseller'),
    path('reseller/rcard/user/passwordreset/<str:username>', views.resetpasswordresellerrcarduser, name='resetpasswordresellerrcarduser'),

    path('subreseller/vcloud/user/passwordreset/<str:username>', views.resetpasswordsubresellervclouduser, name='resetpasswordsubresellervclouduser'),
    path('subreseller/dcard/user/passwordreset/<str:username>', views.resetpasswordsubresellerdcarduser, name='resetpasswordsubresellerdcarduser'),
    path('subreseller/rcard/user/passwordreset/<str:username>', views.resetpasswordsubresellerrcarduser, name='resetpasswordsubresellerrcarduser'),

    path('vcloud/downloadproduct/<int:trid>',views.downloadvcloudresellercards, name='downloadresellervcloudcards'),
    path('vcloud/subreseller/downloadproduct/<int:trid>',views.downloadvcloudsubresellercards, name='downloadsubresellervcloudcards'),
    path('vcloud/user/downloadproduct/<int:trid>',views.downloadvcloudusercards, name='downloaduservcloudcards'),

    path('dcard/downloadproduct/<int:trid>',views.downloaddcardresellercards, name='downloadresellerdcardcards'),
    path('dcard/subreseller/downloadproduct/<int:trid>',views.downloaddcardsubresellercards, name='downloadsubresellerdcardcards'),
    path('dcard/user/downloadproduct/<int:trid>',views.downloaddcardusercards, name='downloaduserdcardcards'),

    path('rcard/downloadproduct/<int:trid>',views.downloadrcardresellercards, name='downloadresellerrcardcards'),
    path('rcard/subreseller/downloadproduct/<int:trid>',views.downloadrcardsubresellercards, name='downloadsubresellerrcardcards'),
    path('rcard/user/downloadproduct/<int:trid>',views.downloadrcardusercards, name='downloaduserrcardcards'),


    path('vcloudcards/downloads/<int:id>',views.vcloudcardsdownloads, name="vcloudcardsdownloads"),
    path('dcardcards/downloads/<int:id>',views.dcardcardsdownloads, name="dcardcardsdownloads"),
    path('rcardcards/downloads/<int:id>',views.rcardcardsdownloads, name="rcardcardsdownloads"),

    path('user/vcloud/paymentreport',views.uservcloudpaymentreport, name="userpaymentreport"),
    path('user/vcloud/paymentreport/filter',views.filteruservcloudpaymentreport, name="filteruservcloudpaymentreport"),
    path('user/dcard/paymentreport',views.userdcardpaymentreport, name="userdcardpaymentreport"),
    path('user/dcard/paymentreport/filter',views.filteruserdcardpaymentreport, name="filteruserdcardpaymentreport"),
    path('user/rcard/paymentreport',views.userrcardpaymentreport, name="userrcardpaymentreport"),
    path('user/rcard/paymentreport/filter',views.filteruserrcardpaymentreport, name="filteruserrcardpaymentreport"),

    path('vcloud/brands/delete/<int:id>',views.deleteVcloudBrands, name="vcloudbrandsdelete"),
    path('dcard/brands/delete/<int:id>',views.deleteDcardBrands, name="dcardbrandsdelete"),
    path('rcard/brands/delete/<int:id>',views.deleteRcardBrands, name="rcardbrandsdelete"),

    path('user/vcloud/btreport',views.uservcloudbtreport, name="uservcloudbtreport"),
    path('user/dcard/btreport',views.userdcardbtreport, name="userdcardbtreport"),
    path('user/rcard/btreport',views.userrcardbtreport, name="userrcardbtreport"),
    path('user/vcloud/btreport/filter',views.filteruservcloudbtreport, name="filteruservcloudbtreport"),
    path('user/dcard/btreport/filter',views.filteruserdcardbtreport, name="filteruserdcardbtreport"),
    path('user/rcard/btreport/filter',views.filteruserrcardbtreport, name="filteruserrcardbtreport"),
    #___________________________________________________________API_______________________________________________________

    path('api/login',views.apiLogin),
    #path('api/GetAllResellerList', views.apiGetAllResellerList),
    path('api/GetAllUserList', views.apiGetAllUserList),
    path('api/GetSingleUserDetails', views.apiGetSingleUserDetails),
    path('api/BalanceTransfer', views.apiBalanceTransfer),
    path('api/FundTransfer', views.apiFundTransfer),
    path('api/BalanceTransferHistory', views.apiGetBalanceTransactionHistory),
    path('api/FundTransferHistory', views.apiGetFundTransactionHistory),
    path('api/ChangePassword', views.apiChangePassword),
    path('api/ResetPassword', views.apiResetPassword),
    path('api/GetCreditBalance', views.apiGetCreditBalance),

    path('api/GetVoipStore', views.apiGetVoipStore),
    path('api/GetFilteredVoipStore', views.apiGetFilteredVoipStore),
    #path('api/GetOwnBrandList', views.apiGetOwnBrandList),
    path('api/GetPurchase', views.apiGetPurchase),
    path('api/GetPurchaseReport', views.apiGetPurchaseReport),
    path('api/GetPurchasedProductReport', views.apiGetPurchasedProductReport),
    path('api/GetFilteredTransactionReport', views.apiGetFilteredTransactionReport),
    path('api/GetFilteredBalanceTransactionHistory', views.apiGetFilteredBalanceTransactionHistory),
    path('api/GetFilteredFundTransactionHistory', views.apiGetFilteredFundTransactionHistory),
    path('api/GetToFundTransactionHistory', views.apiGetToBalanceTransactionHistory),
    path('api/GetToBalanceTransactionHistory', views.apiGetToFundTransactionHistory),
    path('api/GetFilteredToBalanceTransactionHistory', views.apiGetFilteredToBalanceTransactionHistory),
    path('api/GetFilteredToFundTransactionHistory', views.apiGetFilteredToFundTransactionHistory),

    path('api/GetDcardStore', views.apiGetDcardStore),
    path('api/GetFilteredDcardStore', views.apiGetFilteredDcardStore),
    path('api/GetDcardOwnBrandList', views.apiGetDcardOwnBrandList),
    path('api/GetDcardPurchase', views.apiGetDcardPurchase),
    path('api/GetDcardPurchaseReport', views.apiGetDcardPurchaseReport),
    #path('api/GetPurchasedDcardProductReport', views.apiGetPurchasedDcardProductReport),
    #path('api/GetFilteredDcardTransactionReport', views.apiGetDcardFilteredTransactionReport),

    path('api/GetRcardStore', views.apiGetRcardStore),
    path('api/GetFilteredRcardStore', views.apiGetFilteredRcardStore),
    path('api/GetRcardOwnBrandList', views.apiGetRcardOwnBrandList),
    path('api/GetRcardPurchase', views.apiGetRcardPurchase),
    path('api/GetRcardPurchaseReport', views.apiGetRcardPurchaseReport),
    #path('api/GetPurchasedRcardProductReport', views.apiGetPurchasedRcardProductReport),
    #path('api/GetFilteredRcardTransactionReport', views.apiGetRcardFilteredTransactionReport),

    #path('api/docs/', include_docs_urls(title='Voip Cloud Api',authentication_classes=[],permission_classes=[])),

    path('vcloud/addAds', views.addAdvertisements,name="addads"),
    path('vcloud/addAds/submit', views.submitadvertisements,name="submitads"),
    path('vcloud/addAds/view', views.viewAds, name="viewad"),
    path('vcloud/ads/delete/<int:id>',views.deleteAds, name='deleteAds'),

    path('dcard/addAds', views.dcardaddAdvertisements,name="dcardaddads"),
    path('dcard/addAds/submit', views.dcardsubmitadvertisements,name="dcardsubmitads"),
    path('dcard/addAds/view', views.dcardviewAds, name="dcardviewad"),
    path('dcard/ads/delete/<int:id>',views.dcarddeleteAds, name='dcarddeleteAds'),

    path('rcard/addAds', views.rcardaddAdvertisements,name="rcardaddads"),
    path('rcard/addAds/submit', views.rcardsubmitadvertisements,name="rcardsubmitads"),
    path('rcard/addAds/view', views.rcardviewAds, name="rcardviewad"),
    path('rcard/ads/delete/<int:id>',views.rcarddeleteAds, name='rcarddeleteAds'),

    #path('api/GetImageAds', views.apiGetImageAdvertisements),
    path('api/GetAds', views.apiGetTextAdvertisements),

    path('vcloud/product/delete/<int:id>',views.deleteVcloudProduct, name='deletevcloudproduct'),
    path('dcard/product/delete/<int:id>',views.deleteDcardProduct, name='deletedcardproduct'),
    path('rcard/product/delete/<int:id>',views.deleteRcardProduct, name='deletercardproduct'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
