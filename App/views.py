from django.shortcuts import render,render_to_response,redirect,get_object_or_404
from django.http import HttpResponse, HttpResponseNotFound, Http404,  HttpResponseRedirect, JsonResponse
from App.forms import *
from django.contrib import messages
from App.models import *
from App.serializers import *
from django.core import serializers
from django.forms.models import model_to_dict
from decimal import Decimal
from django.db.models import Sum, Count
import json
import hashlib
from django.shortcuts import render,render_to_response,redirect,get_object_or_404
from django.http import HttpResponse, HttpResponseNotFound, Http404,  HttpResponseRedirect, JsonResponse
from App.forms import *
from django.contrib import messages
from django.utils.formats import localize
from App.models import *
from App.serializers import *
from django.core import serializers
from django.forms.models import model_to_dict
from decimal import Decimal
from django.db.models import Sum, Count
import json
import hashlib
from django.db import connection
from itertools import groupby
from operator import itemgetter
import itertools
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from django.conf import settings
from datetime import datetime, timedelta, date
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, renderers, response, schemas
from wsgiref.util import FileWrapper
import os, Project.settings
import mimetypes
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes, renderer_classes, schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK,
    HTTP_405_METHOD_NOT_ALLOWED,
    HTTP_204_NO_CONTENT,
    HTTP_302_FOUND,
    HTTP_406_NOT_ACCEPTABLE,
    HTTP_202_ACCEPTED,
    HTTP_403_FORBIDDEN,
    HTTP_401_UNAUTHORIZED,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from rest_framework.response import Response
import coreapi, coreschema
from rest_framework.schemas import AutoSchema, ManualSchema
from django.db.models import Q
import pytz

def PageNotFound(request):
    response = render_to_response('404.html')
    response.status_code = 404
    return response

def ServerError(request):
    response = render_to_response('500.html')
    response.status_code = 505
    return response
# Create your views here.

def LoginPage(request):
    if request.session.has_key("user"):
        usertype=request.session['usertype']
        if(usertype=="Admin"):
            return redirect(vcloudhomePage)
            #return redirect(databasefix)
        elif(usertype=="Reseller"):
            return redirect(resellervcloudStore)
        elif(usertype=="Sub_Reseller"):
            return redirect(subresellervcloudStore)
        elif(usertype=="User"):
            return redirect(uservcloudStore)
        else:
            return render(request,"index.html",{'form':UserLoginForm})
    else:
        return render(request,"index.html",{'form':UserLoginForm})

def LoginSubmit(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST or None)
        print(form.errors)
        if form.is_valid():
            username=form.cleaned_data.get("username")
            password=form.cleaned_data.get("password")
            hashkey = username+password
            hash = hashlib.sha256(hashkey.encode()).hexdigest()
            if (UserData.objects.filter(username = username, password = hash)).exists():
                user = UserData.objects.get(username = username, password = hash)
                if(user.status):
                    request.session["user"] = user.username
                    request.session["usertype"] = user.postId
                    print(user)
                    if(user.postId=="Admin"):
                        return redirect(vcloudhomePage)
                    elif(user.postId=="Reseller"):
                        return redirect(resellervcloudStore)
                    elif(user.postId=="Sub_Reseller"):
                        return redirect(subresellervcloudStore)
                    else:
                        return redirect(uservcloudStore)
                else:
                    messages.warning(request, 'You Are Blocked By Someone, Contact with your Administrator')
                    return redirect(LoginPage)
            else:
                messages.warning(request, 'Incorrect Username Or Password')
                return redirect(LoginPage)
        else:
            form = UserLoginForm()
            return render(request,"index.html",{'form':UserLoginForm})

    else:
        form = UserLoginForm()
        return render(request,"index.html",{'form':UserLoginForm})

def logoutclick(request):
    for sesskey in list(request.session.keys()):
        del request.session[sesskey]
    return redirect(LoginPage)
#________________________________________________________________Admin_______________________________________________________________

#________________VCLOUD_______________

def vcloudhomePage(request):
    if request.session.has_key("user"):
        last_month = datetime.today() - timedelta(days=1)
        username = request.session["user"]
        reseller = UserData.objects.filter(sponserId=username,postId="Reseller")
        resellerlist=list()
        for i in reseller:
            resellerdata={'username':i.username,'name':i.name}
            resellerlist.append(resellerdata)
        #print(list(reseller[0]))
        type = request.session["usertype"]
        try:
            user = UserData.objects.get(username = username, postId = type)
        except UserData.DoesNotExist:
            return redirect(LoginPage)
        userdetails = UserData.objects.get(username=request.session["user"])
        username=request.session["user"]
        last_month = datetime.today() - timedelta(days=1)
        vcloudtxns = vcloudtransactions.objects.filter(date__gte=last_month,sponser1__username=username,type="Vcloud").order_by('-date')
        content=list()
        topuser=list()
        noofrecords=0
        productsum =0
        quantitysum =0
        profitsum =0
        count=0
        for i in vcloudtxns:
            count=count+1
            data={"id":i.id,"saleduser":i.sponser2.name,"role":i.sponser2.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(i.denominations*i.quantity),"profit":(i.margin1*i.quantity),"rtype":i.rtype}
            data3={'user':i.sponser2.name,'amount':(i.denominations*i.quantity)}
            topuser.append(data3)
            content.append(data)
            productsum=productsum+(i.denominations*i.quantity)
            quantitysum=quantitysum+i.quantity
            profitsum = profitsum+(i.margin1*i.quantity)
        box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum,'noofrecords':count}
        brand=vcloudBrands.objects.all()
        product=list()
        for j in brand:
            prdcts=vcloudProducts.objects.filter(brand__id=j.id,status=True).order_by("brand__brand").values("brand").annotate(productcount=Count('brand')).values('brand__brand', 'productcount','brand__denomination')
            if(prdcts):
                for k in prdcts:
                    totalcost=k['productcount']*k['brand__denomination']
                    data2={"brand":k['brand__brand'],"count":k['productcount'],"denomination":k['brand__denomination'],'totalcost':totalcost}
                    product.append(data2)
            else:
                totalcost=0
                count=0
                tdenomination=j.denomination
                data2={"brand":j.brand,"count":count,"denomination":tdenomination,'totalcost':totalcost}
                product.append(data2)

        #print(topuser)
        list3=list()
        sorted_users = sorted(topuser, key=itemgetter('user'))

        for key, group in itertools.groupby(sorted_users, key=lambda x:x['user']):
            amountsum=0
            for g in group:
                amountsum=amountsum+g["amount"]
            data5={'user':key,'amount':amountsum}
            list3.append(data5)
        return render(request,"admin/vcloud/dashboard-vcloud.html",{'filterform':vcloudDashboardfilter,'reseller':resellerlist,'recenttransactions':content,'products':product,'user':user,'topuser':list3,'last_month':last_month,'boxval':box_data})
    else:
        return redirect(LoginPage)

def filtervcloudhomepage(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = vcloudDashboardfilter(request.POST or None)
            print(form.errors)
            if form.is_valid():
                currentuser=request.session["user"]
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                usertype=form.cleaned_data.get("usertype")
                uuusername=form.cleaned_data.get("username")
                print(fromdate.strftime("%B %d, %Y"))
                last_month=fromdate.strftime("%B %d, %I:%M %p")+" To "+todate.strftime("%B %d, %I:%M %p")
                reseller = UserData.objects.filter(sponserId=currentuser,postId="Reseller")
                #print(reseller)
                resellerlist=list()
                for i in reseller:
                    resellerdata={'username':i.username,'name':i.name}
                    resellerlist.append(resellerdata)
                #print(username)
                userdetails = UserData.objects.get(username=request.session["user"])
                vcloudtxns = vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate,sponser1__username=currentuser,type="Vcloud",sponser2__username=uuusername).order_by('-date')
                content=list()
                topuser=list()
                noofrecords=0
                productsum =0
                quantitysum =0
                profitsum =0
                count=0
                for i in vcloudtxns:
                    count=count+1
                    data={"id":i.id,"saleduser":i.sponser2.name,"role":i.sponser2.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(i.denominations*i.quantity),"profit":(i.margin1*i.quantity),"rtype":i.rtype}
                    data3={'user':i.sponser2.name,'amount':(i.denominations*i.quantity)}
                    topuser.append(data3)
                    content.append(data)
                    productsum=productsum+(i.denominations*i.quantity)
                    quantitysum=quantitysum+i.quantity
                    profitsum = profitsum+(i.margin1*i.quantity)
                box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum,'noofrecords':count}
                brand=vcloudBrands.objects.all()
                product=list()
                for j in brand:
                    prdcts=vcloudProducts.objects.filter(brand__id=j.id,status=True).order_by("brand__brand").values("brand").annotate(productcount=Count('brand')).values('brand__brand', 'productcount','brand__denomination')
                    #print(prdcts)
                    if(prdcts):
                        for k in prdcts:
                            totalcost=k['productcount']*k['brand__denomination']
                            data2={"brand":k['brand__brand'],"count":k['productcount'],"denomination":k['brand__denomination'],'totalcost':totalcost}
                            product.append(data2)
                    else:
                        totalcost=0
                        count=0
                        tdenomination=j.denomination
                        data2={"brand":j.brand,"count":count,"denomination":tdenomination,'totalcost':totalcost}
                        product.append(data2)
                #print(topuser)
                list3=list()
                sorted_users = sorted(topuser, key=itemgetter('user'))

                for key, group in itertools.groupby(sorted_users, key=lambda x:x['user']):
                    amountsum=0
                    for g in group:
                        amountsum=amountsum+g["amount"]
                        #print(amountsum)
                    data5={'user':key,'amount':amountsum}
                    list3.append(data5)
                return render(request,"admin/vcloud/dashboard-vcloud.html",{'filterform':vcloudDashboardfilter,'reseller':resellerlist,'recenttransactions':content,'products':product,'user':userdetails,'topuser':list3,'last_month':last_month,'boxval':box_data})
            else:
                return redirect(vcloudhomePage)
        else:
            return(vcloudhomePage)
    else:
        return redirect(LoginPage)

def vcloudaddReseller(request):
    if request.session.has_key("user"):
        username = request.session["user"]
        user = UserData.objects.get(username = username)
        return render(request,"admin/vcloud/addReseller.html",{'form':AddUserDataForm,'user':user})
    else:
        return redirect(LoginPage)

def vcloudnewReseller(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = AddUserDataForm(request.POST or None)
            print(form.errors)
            if form.is_valid():
                username=form.cleaned_data.get("username")
                password=form.cleaned_data.get("password")
                hashkey = username+password
                hash = hashlib.sha256(hashkey.encode()).hexdigest()
                sponser = request.session["user"]
                sponseruser=UserData.objects.get(username=sponser)
                Userdata=form.save(commit=False)
                Userdata.postId="Reseller"
                Userdata.sponserId = sponseruser
                Userdata.status = True
                Userdata.balance = 0
                Userdata.targetAmt = 0
                Userdata.rentalAmt = 0
                Userdata.dcard_status = True
                Userdata.rcard_status = True
                Userdata.password = hash
                Userdata.save()
                messages.success(request, 'Successfully Added')
                return redirect(vcloudaddReseller)
            else:
                username = request.session["user"]
                user = UserData.objects.get(username = username)
                form = AddUserDataForm()
                messages.warning(request, 'Internal Error Occur')
                return render(request,"admin/vcloud/addReseller.html",{'form':AddUserDataForm,'user':user})
        else:
            username = request.session["user"]
            user = UserData.objects.get(username = username)
            form = AddUserDataForm()
            return render(request,"admin/vcloud/addReseller.html",{'form':AddUserDataForm,'user':user})
    else:
        return redirect(LoginPage)

def vcloudviewReseller(request):
    if request.session.has_key("user"):
        resellers = UserData.objects.filter(postId="Reseller")
        username = request.session["user"]
        user = UserData.objects.get(username = username)
        return render(request,"admin/vcloud/viewResellers.html",{'resellers':resellers,'user':user})
    else:
        return redirect(LoginPage)

def vcloudaddUser(request):
    if request.session.has_key("user"):
        username = request.session["user"]
        user = UserData.objects.get(username = username)
        return render(request,"admin/vcloud/addUser.html",{'form':AddUserDataForm,'user':user})
    else:
        return redirect(LoginPage)

def vcloudnewUser(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = AddUserDataForm(request.POST or None)
            print(form.errors)
            if form.is_valid():
                username=form.cleaned_data.get("username")
                password=form.cleaned_data.get("password")
                hashkey = username+password
                hash = hashlib.sha256(hashkey.encode()).hexdigest()
                print(username)
                print(password)
                print(hash)
                sponser = request.session["user"]
                sponseruser=UserData.objects.get(username=sponser)
                Userdata=form.save(commit=False)
                Userdata.postId="User"
                Userdata.sponserId = sponseruser
                Userdata.status = True
                Userdata.balance = 0
                Userdata.targetAmt = 0
                Userdata.rentalAmt = 0
                Userdata.dcard_status = True
                Userdata.rcard_status = True
                Userdata.password = hash
                Userdata.save()
                messages.success(request, 'Successfully Added')
                return redirect(vcloudaddUser)
            else:
                username = request.session["user"]
                user = UserData.objects.get(username = username)
                messages.warning(request, 'Internal Error Occured')
                form = AddUserDataForm()
                return render(request,"admin/vcloud/addUser.html",{'form':AddUserDataForm,'user':user})
        else:
            username = request.session["user"]
            user = UserData.objects.get(username = username)
            form = AddUserDataForm()
            return render(request,"admin/vcloud/addUser.html",{'form':AddUserDataForm,'user':user})
    else:
        return redirect(LoginPage)

def vcloudviewUser(request):
    if request.session.has_key("user"):
        user = request.session["user"]
        userdet = UserData.objects.get(username = user)
        resellers = UserData.objects.filter(postId="User",sponserId=user)
        #request.session['_old_post'] = request.GET

        return render(request,"admin/vcloud/viewUser.html",{'resellers':resellers,'user':userdet})
    else:
        return redirect(LoginPage)

def vcloudprofile(request):
    if request.session.has_key("user"):
        user = request.session["user"]
        userDet = UserData.objects.get(username=user)
        return render(request,"admin/vcloud/editProfile.html",{'user':userDet})
    else:
        return redirect(LoginPage)

def vcloudeditProfile(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            user = request.session["user"]
            name = request.POST.get('name', None)
            address = request.POST.get('address', None)
            email = request.POST.get('email', None)
            mobileno = request.POST.get('mobileno', None)
            userDet = UserData.objects.get(username=user)
            userDet.name = name
            userDet.address = address
            userDet.email = email
            userDet.mobileno = mobileno
            userDet.save()
            messages.success(request, 'Successfully Updated')
            return redirect(vcloudprofile)
        else:
            messages.warning(request,'Internal Error Occured')
            return redirect(vcloudprofile)
    else:
        return redirect(LoginPage)

def vcloudbalanceTransfer(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        bthist=balanceTransactionReport.objects.filter(source=userdetails,category="BT").order_by('-date')
        #print(bthist)
        return render(request,"admin/vcloud/balanceTransfer.html",{'bthist':bthist,'user':userdetails})
    else:
        return redirect(LoginPage)

def validate_username(request):
    username = request.GET.get('username', None)
    data = {
        'is_taken': UserData.objects.filter(username__iexact=username).exists()
    }
    return JsonResponse(data)

def getReseller_UserList(request):
    if request.session.has_key("user"):
        usertype = request.GET.get('usertype', None)
        user = request.session['user']
        userlist = UserData.objects.filter(sponserId=user,postId=usertype)
        data = serializers.serialize('json', userlist)
        return HttpResponse(data, content_type="application/json")
    else:
        return redirect(LoginPage)

def getBrandWithTypes(request):
    type = request.GET.get('type', None)
    if(type=="Vcloud"):
        brandlist = vcloudBrands.objects.all()
        data = serializers.serialize('json', brandlist)
        return HttpResponse(data, content_type="application/json")
    elif(type=="Dcard"):
        brandlist = dcardBrands.objects.all()
        data = serializers.serialize('json', brandlist)
        return HttpResponse(data, content_type="application/json")
    else:
        brandlist = rcardBrands.objects.all()
        data = serializers.serialize('json', brandlist)
        return HttpResponse(data, content_type="application/json")

def getCreditBalance(request):
    try:
        user = request.GET.get('users', None)
        credit=UserData.objects.get(username=user)
        return JsonResponse(model_to_dict(credit))
    except:
        return redirect(LoginPage)

def vcloudSubmitBalanceTransfer(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            userType = request.POST.get('userType', None)
            user = request.POST.get('users', None)
            amount = request.POST.get('amount', None)
            userdet = UserData.objects.get(username=user)
            bal = userdet.balance
            newbal=bal+Decimal(amount)
            cdbal = userdet.targetAmt
            newcdbal = cdbal-Decimal(amount)
            userdet.targetAmt = newcdbal
            userdet.balance = newbal
            userdet.save()
            userdetails = UserData.objects.get(username=request.session["user"])
            btreport = balanceTransactionReport()
            btreport.source = userdetails
            btreport.destination = userdet
            btreport.category = "BT"
            btreport.pbalance = bal
            btreport.nbalance = newbal
            btreport.cramount = newcdbal
            btreport.amount = amount
            btreport.remarks = 'Added To Balance'
            btreport.save()
            messages.success(request, 'Successfully Updated The balance')
            return redirect(vcloudbalanceTransfer)
            #userdata=UserData.objects.get(username=)
        else:
            messages.warning(request, 'Internal Error Occured')
            return redirect(vcloudbalanceTransfer)
    else:
        return redirect(LoginPage)


def vcloudaddPayment(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        phist=fundTransactionReport.objects.filter(source=userdetails).order_by('-date')
        return render(request,"admin/vcloud/addPayment.html",{'phist':phist,'user':userdetails})
    else:
        return redirect(LoginPage)

def vcloudsubmitPayment(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            userType = request.POST.get('userType', None)
            user = request.POST.get('users', None)
            amount = request.POST.get('amount', None)
            remarks = request.POST.get('remarks', None)
            userdet = UserData.objects.get(username=user)
            obalance = userdet.targetAmt
            cdbal = userdet.targetAmt
            newcdbal = cdbal+Decimal(amount)
            userdet.targetAmt = newcdbal
            userdet.save()
            closeuser = UserData.objects.get(username=user)
            userdetails = UserData.objects.get(username=request.session["user"])
            ftreport=fundTransactionReport()
            ftreport.source = userdetails
            ftreport.destination = userdet
            ftreport.obalance = obalance
            ftreport.cbalance = closeuser.targetAmt
            ftreport.role = userType
            ftreport.amount = amount
            ftreport.balance = newcdbal
            ftreport.remarks = remarks
            ftreport.save()
            messages.success(request, 'Successfully Updated The balance')
            return redirect(vcloudaddPayment)
        else:
            messages.warning(request, 'Internal error Occured')
            return redirect(vcloudaddPayment)
    else:
        return redirect(LoginPage)

def vcloudbalanceTransferReport(request):
    if request.session.has_key("user"):
        username = request.session["user"]
        userdetails = UserData.objects.get(username=request.session["user"])
        reseller = UserData.objects.filter(sponserId=username,postId="Reseller")
        sum = balanceTransactionReport.objects.filter(source=userdetails,category='BT').aggregate(Sum('amount'))
        bthist = balanceTransactionReport.objects.filter(source=userdetails).order_by('-date')
        return render(request,"admin/vcloud/balanceTransferReport.html",{'form':balancetransferfilterform,'reseller':reseller,'bthist':bthist,'sum':sum['amount__sum'],'user':userdetails})
    else:
        return redirect(LoginPage)

def filtervcloudbtreport(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            form = balancetransferfilterform(request.POST or None)
            print(form.errors)
            if form.is_valid():
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                usertype=form.cleaned_data.get("usertype")
                susername=form.cleaned_data.get("username")
                username = request.session["user"]
                #fuser=UserData.objects.get(username=susername)
                filter={'ffdate':fromdate,'ttdate':todate,'fuser':susername}
                userdetails = UserData.objects.get(username=request.session["user"])
                reseller = UserData.objects.filter(sponserId=username,postId="Reseller")
                sum=None
                bthist=None
                try:
                    if(usertype == "All" and susername == "All"):
                        sum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails).aggregate(Sum('amount'))
                        bthist = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails)
                    elif(usertype!="All" and susername == "All"):
                        sum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails, destination__postId=usertype).aggregate(Sum('amount'))
                        bthist = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails, destination__postId=usertype)
                    else:
                        sum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__username=susername).aggregate(Sum('amount'))
                        bthist = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__username=susername)
                except:
                    pass
                return render(request,"admin/vcloud/balanceTransferReport.html",{'form':balancetransferfilterform,'reseller':reseller,'bthist':bthist,'sum':sum['amount__sum'],'user':userdetails,'filter':filter})
            else:
                return redirect(vcloudbalanceTransferReport)
        else:
            return redirect(vcloudbalanceTransferReport)
    else:
        return redirect(LoginPage)

def vcloudpaymentReport(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        reseller = UserData.objects.filter(sponserId=request.session["user"],postId="Reseller")
        phist = fundTransactionReport.objects.filter(source=userdetails).order_by('-date')
        bsum = fundTransactionReport.objects.filter(source=userdetails).aggregate(Sum('amount'))
        return render(request,"admin/vcloud/paymentReport.html",{'form':paymentfilterform,'reseller':reseller,'phist':phist,'sum':bsum['amount__sum'],'user':userdetails})
    else:
        return redirect(LoginPage)

def filtervcloudpaymentreport(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            form = balancetransferfilterform(request.POST or None)
            print(form.errors)
            if form.is_valid():
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                usertype=form.cleaned_data.get("usertype")
                susername=form.cleaned_data.get("username")
                username = request.session["user"]
                #fuser=UserData.objects.get(username=susername)
                filter={'ffdate':fromdate,'ttdate':todate,'fuser':susername}
                userdetails = UserData.objects.get(username=request.session["user"])
                reseller = UserData.objects.filter(sponserId=username,postId="Reseller")
                sum=None
                bthist=None
                try:
                    if(usertype == "All" and susername == "All"):
                        bsum = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails).aggregate(Sum('amount'))
                        phist = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails)
                    elif(usertype!="All" and susername == "All"):
                        bsum = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails, destination__postId=usertype).aggregate(Sum('amount'))
                        phist = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails, destination__postId=usertype)
                    else:
                        bsum = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__username=susername).aggregate(Sum('amount'))
                        phist = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__username=susername)
                except:
                    pass
                return render(request,"admin/vcloud/paymentReport.html",{'form':paymentfilterform,'reseller':reseller,'phist':phist,'sum':bsum['amount__sum'],'user':userdetails,'filter':filter})
            else:
                return redirect(vcloudpaymentReport)
        else:
            return redirect(vcloudpaymentReport)
    else:
        return redirect(LoginPage)


def addVcloudBrand(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"admin/vcloud/addVcloudBrand.html",{'form':AddVcloudBrands,'user':userdetails})
    else:
        return redirect(LoginPage)

def vcloudeditResellerView(request):
    user = request.GET.get('username', None)
    userdet=UserData.objects.get(username=user)
    return JsonResponse(model_to_dict(userdet))

def adminVcloudDashboard(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"dashboard-vcloud.html",{'user':userdetails})
    else:
        return redirect(LoginPage)

def submitVcloudBrands(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = AddVcloudBrands(request.POST, request.FILES)
            #print(form.errors)
            if form.is_valid():
                branddata=form.save()
                messages.success(request, 'Successfully Added The Brands')
                return redirect(addVcloudBrand)
            else:
                messages.warning(request, 'Internal Error Occured')
                return redirect(addVcloudBrand)
        else:
            return redirect(addVcloudBrand)
    else:
        return redirect(LoginPage)

def manageVcloudBrands(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        brands = vcloudBrands.objects.all()
        return render(request,"admin/vcloud/manageVcloudBrand.html",{'brands':brands,'user':userdetails})
    else:
        return redirect(LoginPage)

def assignVcloudBrands(request):
    if request.session.has_key("user"):
        brands = vcloudBrands.objects.all()
        #brands = vcloudProducts.objects.filter(status=True).order_by('brand').values('brand').annotate(count=Count('brand')).values('brand__id','brand__brand','brand__denomination','count','brand__description','brand__logo','brand__currency','brand__category')
        print(brands)
        userdetails = UserData.objects.get(username=request.session["user"])
        resellers = UserData.objects.filter(postId="Reseller")
        return render(request,"admin/vcloud/assignVcloudBrands.html",{'brands':brands,'resellers':resellers,'user':userdetails})
    else:
        return redirect(LoginPage)

def addVcloudProduct(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        brands = vcloudBrands.objects.filter()
        return render(request,"admin/vcloud/addVcloudProduct.html",{'productform':AddVcloudProducts,'brandform':AddVcloudBrands,'user':userdetails,'brands':brands})
    else:
        return redirect(LoginPage)

def submitVcloudProducts(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            try:
                form = AddVcloudProducts(request.POST or None)
                if form.is_valid():
                    brandid = form.cleaned_data.get("brand")
                    username = form.cleaned_data.get("username")
                    password = form.cleaned_data.get("password")
                    res=vcloudProducts.objects.filter(username = username).exists()
                    print(res)
                    res1=vcloudupproducts.objects.filter(username = username).exists()
                    print(res1)
                    if(res or res1):
                        messages.warning(request, 'Product is alreday updated in Csv log. Go and spent the product')
                    else:
                        product = vcloudProducts()
                        branddet = vcloudBrands.objects.get(id=brandid)
                        product.brand = branddet
                        product.username = username
                        product.password = password
                        product.denomination = branddet.denomination
                        product.save()
                        messages.success(request, 'Successfully Added The Products')
                    return redirect(addVcloudProduct)
                else:
                    messages.warning(request, form.errors)
                    return redirect(addVcloudProduct)
            except:
                return redirect(addVcloudProduct)
        else:
            return redirect(addVcloudProduct)
    else:
        return redirect(LoginPage)

def getBrandDetails(request):
    id = request.GET.get('id', None)
    brdet = vcloudBrands.objects.get(id=id)
    data={"id":brdet.id,"brand":brdet.brand,"logo":brdet.logo.url,"rate":brdet.denomination,"desc":brdet.description}
    return JsonResponse(data)

def getProductDetails(request):
    id = request.GET.get('id', None)
    brdet = vcloudProducts.objects.get(id=id)
    data={"id":brdet.id,"brand":brdet.brand.brand,"logo":brdet.brand.logo.url,"rate":brdet.brand.denomination,"desc":brdet.brand.description,"username":brdet.username,"password":brdet.password,"status":brdet.status}
    #print(data)
    return JsonResponse(data)

def getDatacardProductDetails(request):
    id = request.GET.get('id', None)
    brdet = datacardproducts.objects.get(id=id)
    data={"id":brdet.id,"brand":brdet.brand.brand,"logo":brdet.brand.logo.url,"rate":brdet.brand.denomination,"desc":brdet.brand.description,"username":brdet.username,"status":brdet.status}
    #print(data)
    return JsonResponse(data)

def getRcardProductDetails(request):
    id = request.GET.get('id', None)
    brdet = rcardProducts.objects.get(id=id)
    data={"id":brdet.id,"brand":brdet.brand.brand,"logo":brdet.brand.logo.url,"rate":brdet.brand.denomination,"desc":brdet.brand.description,"username":brdet.username,"status":brdet.status}
    #print(data)
    return JsonResponse(data)

def submitManageBrands(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = editVcloudBrands(request.POST, request.FILES)
            if form.is_valid():
                id = form.cleaned_data.get("id")
                brandname = form.cleaned_data.get("brand")
                flag=True;
                brand = vcloudBrands.objects.get(id=id)
                try:
                    logo = request.FILES['logo']
                    brand.logo = logo
                    print(logo)
                except:
                    flag=False;
                description = form.cleaned_data.get("desc")
                denomination = form.cleaned_data.get("rate")
                brand.brand = brandname
                brand.description = description
                brand.denomination = denomination
                brand.save()
                print(brand)
                return redirect(manageVcloudBrands)
            else:
                print(form.errors)
                return redirect(manageVcloudBrands)
        else:
            return redirect(manageVcloudBrands)
    else:
        return redirect(LoginPage)

def editsubmitManageProducts(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = EditVcloudProducts(request.POST, request.FILES)
            if form.is_valid():
                id = form.cleaned_data.get("id")
                username = form.cleaned_data.get("username")
                password = form.cleaned_data.get("password")
                flag=True;
                brand = vcloudProducts.objects.get(id=id)
                brand.username = username
                brand.password = password
                brand.save()
                print(brand)
                return redirect(vcloudmanageProduct)
            else:
                print(form.errors)
                return redirect(vcloudmanageProduct)
        else:
            return redirect(vcloudmanageProduct)
    else:
        return redirect(LoginPage)

def editsubmitManagedcardProducts(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = EditCardProducts(request.POST, request.FILES)
            if form.is_valid():
                id = form.cleaned_data.get("id")
                username = form.cleaned_data.get("username")
                #password = form.cleaned_data.get("password")
                flag=True;
                brand = datacardproducts.objects.get(id=id)
                brand.username = username
                #brand.password = password
                brand.save()
                print(brand)
                return redirect(dcardmanageProduct)
            else:
                print(form.errors)
                return redirect(dcardmanageProduct)
        else:
            return redirect(dcardmanageProduct)
    else:
        return redirect(LoginPage)

def editsubmitManagercardProducts(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = EditCardProducts(request.POST, request.FILES)
            if form.is_valid():
                id = form.cleaned_data.get("id")
                username = form.cleaned_data.get("username")
                #password = form.cleaned_data.get("password")
                flag=True;
                brand = rcardProducts.objects.get(id=id)
                brand.username = username
                #brand.password = password
                brand.save()
                print(brand)
                return redirect(rcardmanageProduct)
            else:
                print(form.errors)
                return redirect(rcardmanageProduct)
        else:
            return redirect(rcardmanageProduct)
    else:
        return redirect(LoginPage)

def editReseller(request):
    username = request.GET.get('username', None)
    usrdet = UserData.objects.get(username=username)
    print(username)
    data = {"username":usrdet.username,"name":usrdet.name,"address":usrdet.address,"email":usrdet.email, "mobile":usrdet.mobileno, "retailerLimit":usrdet.retailerLimit ,"balance":usrdet.balance,"margin":usrdet.margin,"ior":usrdet.recharge_status,"vcloud":usrdet.vcloud_status,"status":usrdet.status}
    return JsonResponse(data)

def submitEditUsers(request):
    name = request.GET.get('name', None)
    username = request.GET.get('username', None)
    email = request.GET.get('email', None)
    mobileno = request.GET.get('mobileno', None)
    balance = request.GET.get('balance', None)
    margin = request.GET.get('margin', None)
    transactionlimit = request.GET.get('transactionlimit', None)
    recharge_status = request.GET.get('recharge_status', None)
    vcloud_status = request.GET.get('vcloud_status', None)
    usrdet = UserData.objects.get(username=username)
    usrdet.name = name
    usrdet.email = email
    usrdet.mobileno = mobileno
    usrdet.balance = balance
    usrdet.margin = margin
    usrdet.retailerLimit = transactionlimit
    if(recharge_status=="true"):
        usrdet.recharge_status = True
    else:
        usrdet.recharge_status = False
    if(vcloud_status=="false"):
        usrdet.vcloud_status = False
    else:
        usrdet.vcloud_status = True
    usrdet.save()
    data = {"status":"Success"}
    return JsonResponse(data)

def vcloudStore(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        pdcts = vcloudProducts.objects.filter(status=True,brand__category="card with cutting").order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
        ads = adverisements.objects.filter(adtype="Image",ctype="Vcloud").order_by('-id')[:10]
        buttonlist=["Cutting","Non Cutting"]
        buttonclass=["btn-warning","btn-success"]
        btnlist = zip(buttonlist, buttonclass)
        return render(request,"admin/vcloud/vcloudStore.html",{'pdcts':pdcts,'btnlist':btnlist,'user':userdetails,'ads':ads})
    else:
        return redirect(LoginPage)

def filteredvcloudstore(request,brandtype):
    if request.session.has_key("user"):
        ads = adverisements.objects.filter(adtype="Image",ctype="Vcloud").order_by('-id')[:10]
        buttonclass=[]
        userdetails = UserData.objects.get(username=request.session["user"])
        if(brandtype=="Cutting"):
            pdcts = vcloudProducts.objects.filter(status=True,brand__category="card with cutting").order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
            buttonclass=["btn-warning","btn-success"]
        else:
            pdcts = vcloudProducts.objects.filter(status=True,brand__category="card without cutting").order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
            buttonclass=["btn-success","btn-warning"]
        buttonlist=["Cutting","Non Cutting"]
        btnlist = zip(buttonlist, buttonclass)
        return render(request,"admin/vcloud/vcloudStore.html",{'pdcts':pdcts,'btnlist':btnlist,'user':userdetails,'ads':ads})
    else:
        return redirect(LoginPage)

def saveassignVcloudBrands(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            try:
                reseller = request.POST.get('username', None)
                values = request.POST.get('values', None)
                states = request.POST.get('states', None)
                brands = request.POST.get('brands', None)
                margins = request.POST.get('margins', None)
                v = values.split(',')
                s = states.split(',')
                b = brands.split(',')
                m = margins.split(',')
                username = request.session["user"]
                assignedby = UserData.objects.get(username=username)
                assignedto = UserData.objects.get(username=reseller)
                #print(len(s))
                for i in range(0,len(s)):
                    if(int(s[i])==0):
                        print(True)
                        brandid=b[i]
                        brdet=vcloudBrands.objects.get(id=brandid)
                        print(brdet)
                        try:
                            vdt = vcloudAssignments.objects.get(brand=brdet,assignedby=assignedby,assignedto=assignedto)
                            print(vdt)
                            vdt.delete()
                            print(assignedto)
                            vadt = vcloudAssignments.objects.filter(brand=brdet,assignedby=assignedto)
                            print(vadt)
                            for i in vadt:
                                try:
                                    ud = vcloudAssignments.objects.filter(brand=brdet,assignedby=i.assignedto)
                                    ud.delete()
                                except Exception as e:
                                    print("inner "+str(e))
                            print(vadt)
                            vadt.delete()
                        except Exception as e:
                            print("Outer "+str(e))
                    else:
                        print(False)
                        brandid=b[int(i)]
                        brdet=vcloudBrands.objects.get(id=brandid)
                        try:
                            assdet = vcloudAssignments.objects.get(brand=brdet,assignedby=assignedby,assignedto=assignedto)
                            assdet.margin = Decimal(v[int(i)])
                            assdet.save()
                        except vcloudAssignments.DoesNotExist:
                            vass = vcloudAssignments()
                            vass.brand=brdet
                            vass.assignedto=assignedto
                            vass.assignedby=assignedby
                            vass.margin = Decimal(v[int(i)])
                            vass.save()
                data={"status":"Success"}
                return JsonResponse(data)
            except Exception as e:
                print("Outer Most"+str(e))
                return JsonResponse({"status":"Error"})
        else:
            return JsonResponse({"status":"Error"})
    else:
        return redirect(LoginPage)

def vcloudmanageProduct(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        product = vcloudProducts.objects.all().order_by('-cdate')[:5000]
        return render(request,"admin/vcloud/manageProduct.html",{'products':product,'user':userdetails})
    else:
        return redirect(LoginPage)

def getSponserDeT(user):
    #print(user)
    usdet=UserData.objects.get(username=user)
    #print(usdet)
    return usdet

def vcloudreport(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        username=request.session["user"]
        last_month = datetime.today() - timedelta(days=1)
        vcloudtxns = vcloudtransactions.objects.filter(date__gte=last_month,sponser1__username=username).order_by('-date')
        #vcloudtxns = vcloudtransactions.objects.all().order_by('-date')
        reseller=UserData.objects.filter(sponserId=username,postId="Reseller")
        resellerlist=list()
        vcbrand=vcloudBrands.objects.all()
        vcbrandlist=list()
        for b in vcbrand:
            branddata={'brand':b.brand}
            vcbrandlist.append(branddata)

        for i in reseller:
            resellerdata={'username':i.username,'name':i.name}
            resellerlist.append(resellerdata)
        content=list()
        noofrecords=0
        productsum =0
        quantitysum =0
        profitsum =0
        for i in vcloudtxns:
            data={"id":i.id,"saleduser":i.sponser2.name,"role":i.sponser2.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(i.denominations*i.quantity),"profit":(i.margin1*i.quantity),"rtype":i.rtype}
            content.append(data)
            productsum=productsum+(i.denominations*i.quantity)
            quantitysum=quantitysum+i.quantity
            profitsum = profitsum+(i.margin1*i.quantity)
        box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum}
        return render(request,"admin/vcloud/vcloudreport.html",{'filterform':vcloudreportfilterform,'products':content,'user':userdetails,'reseller':resellerlist, 'brand':vcbrandlist,'box':box_data,'date':last_month})
    else:
        return redirect(LoginPage)

def filtervcloud_report(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            form = vcloudreportfilterform(request.POST or None)
            print(form.errors)
            if form.is_valid():
                username=request.session["user"]
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                usertype=form.cleaned_data.get("usertype")
                print(usertype)
                fusername=form.cleaned_data.get("username")
                type=form.cleaned_data.get("type")
                brand=form.cleaned_data.get("brand")
                userdetails = UserData.objects.get(username=request.session["user"])
                fuser=''
                if(fusername!='All'):
                    filterdata=UserData.objects.get(username=fusername)
                    fuser=filterdata.name
                else:
                    fuser=fusername
                filter={'ffdate':fromdate,'ttdate':todate,'fuser':fuser}
                reseller=UserData.objects.filter(sponserId=username,postId="Reseller")
                resellerlist=list()
                vcbrand=vcloudBrands.objects.all()
                vcbrandlist=list()
                for b in vcbrand:
                    branddata={'brand':b.brand}
                    vcbrandlist.append(branddata)

                for i in reseller:
                    resellerdata={'username':i.username,'name':i.name}
                    resellerlist.append(resellerdata)

                content=list()
                noofrecords = 0
                productsum = 0
                quantitysum = 0
                profitsum = 0
                vcloudtxns=vcloudtransactions()
                try:
                    print(usertype)
                    print(fusername)
                    print(type)
                    print(brand)
                    if(usertype=="All" and fusername=="All" and type=="All" and brand=="All"):
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser1__username=username).order_by('-date')
                        print("One")
                    elif(usertype=="All" and fusername=="All" and type=="All" and brand !="All"):
                        print("TWo")
                        vcloudtxns==vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser1__username=username, brand=brand).order_by('-date')
                    elif(usertype=="All" and fusername=="All" and type !="All" and brand =="All"):
                        print("Three")
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser1__username=username, type=type).order_by('-date')
                    elif(usertype=="All" and fusername=="All" and type !="All" and brand !="All"):
                        print("four")
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser1__username=username, brand=brand).order_by('-date')
                    elif(usertype=="All" and fusername!="All" and type !="All" and brand !="All"):
                        print('five')
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, type=type, sponser1__username=username, sponser2__username=fusername, brand=brand).order_by('-date')
                    elif(usertype !="All" and fusername =="All" and type =="All" and brand !="All"):
                        print('Six')
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser2__type=usertype, sponser1__username=username).order_by('-date')
                    elif(usertype !="All" and fusername =="All" and type =="All" and brand =="All"):
                        print('Six')
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser1__username=username, sponser2__postId=usertype).order_by('-date')
                    elif(usertype =="All" and fusername !="All" and type =="All" and brand =="All"):
                        print('Six')
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser1__username=username, sponser2__username=fusername).order_by('-date')
                    elif(usertype !="All" and fusername !="All" and type =="All" and brand =="All"):
                        print('Six')
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser1__username=username, sponser2__username=fusername).order_by('-date')
                    else:
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser1__username=username, sponser2__username=fusername,brand=brand).order_by('-date')
                    print(vcloudtxns)
                    for i in vcloudtxns:
                        data={"id":i.id,"saleduser":i.sponser2.name,"role":i.sponser2.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(i.denominations*i.quantity),"profit":(i.margin1*i.quantity),"rtype":i.rtype}
                        content.append(data)
                        productsum=productsum+(i.denominations*i.quantity)
                        quantitysum=quantitysum+i.quantity
                        profitsum = profitsum+(i.margin1*i.quantity)
                except:
                    pass
                box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum}
                return render(request,"admin/vcloud/vcloudreport.html",{'filterform':vcloudreportfilterform,'products':content,'user':userdetails,'reseller':resellerlist, 'brand':vcbrandlist,'box':box_data,'filter':filter})
            else:
                return redirect(vcloudreport)
        else:
            return redirect(vcloudreport)
    else:
        return redirect(LoginPage)

def get_product_details(request):
    if request.session.has_key("user"):
        if request.method == 'POST':
            id = request.POST.get('id', None)
            print(id)
            vcloudtxns=vcloudtransactions.objects.get(id=id)
            print(vcloudtxns)
            type = vcloudtxns.type
            productid=vcloudtxns.product_id
            result = productid.rstrip(',')
            pdid = result.split(',')
            print(pdid)
            pdlist=list()
            content=list()
            if(type=="Vcloud"):
                for i in pdid:
                    pddet=vcloudProducts.objects.get(id=i)
                    data={"id":pddet.id,"brand":pddet.brand.brand,"username":pddet.username,"password":pddet.password}
                    pdlist.append(data)
            elif(type=="Dcard"):
                for i in pdid:
                    pddet=datacardproducts.objects.get(id=i)
                    data={"id":pddet.id,"brand":pddet.brand.brand,"username":pddet.username}
                    pdlist.append(data)
            else:
                for i in pdid:
                    pddet=rcardProducts.objects.get(id=i)
                    data={"id":pddet.id,"brand":pddet.brand.brand,"username":pddet.username}
                    pdlist.append(data)
            content.append(pdlist)
            content.append({"type":type})
            return JsonResponse(content,safe=False)
        else:
            pass
    else:
        return redirect(LoginPage)


#________________DCARD______________

def adminDcardDashboard(request):
    if request.session.has_key("user"):
        last_month = datetime.today() - timedelta(days=1)
        username = request.session["user"]
        reseller = UserData.objects.filter(sponserId=username,postId="Reseller")
        resellerlist=list()
        for i in reseller:
            resellerdata={'username':i.username,'name':i.name}
            resellerlist.append(resellerdata)
        #print(list(reseller[0]))
        type = request.session["usertype"]
        try:
            user = UserData.objects.get(username = username, postId = type)
        except UserData.DoesNotExist:
            return redirect(LoginPage)
        userdetails = UserData.objects.get(username=request.session["user"])
        username=request.session["user"]
        last_month = datetime.today() - timedelta(days=1)
        vcloudtxns = vcloudtransactions.objects.filter(date__gte=last_month,sponser1__username=username,type="Dcard").order_by('-date')
        content=list()
        topuser=list()
        noofrecords=0
        productsum =0
        quantitysum =0
        profitsum =0
        count=0
        for i in vcloudtxns:
            count=count+1
            data={"id":i.id,"saleduser":i.sponser2.name,"role":i.sponser2.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(i.denominations*i.quantity),"profit":(i.margin1*i.quantity),"rtype":i.rtype}
            data3={'user':i.sponser2.name,'amount':(i.denominations*i.quantity)}
            topuser.append(data3)
            content.append(data)
            productsum=productsum+(i.denominations*i.quantity)
            quantitysum=quantitysum+i.quantity
            profitsum = profitsum+(i.margin1*i.quantity)
        box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum,'noofrecords':count}
        brand=dcardBrands.objects.all()
        product=list()
        for j in brand:
            prdcts=datacardproducts.objects.filter(brand__id=j.id,status=True).order_by("brand__brand").values("brand").annotate(productcount=Count('brand')).values('brand__brand', 'productcount','brand__denomination')
            #print(prdcts)
            if(prdcts):
                for k in prdcts:
                    totalcost=k['productcount']*k['brand__denomination']
                    data2={"brand":k['brand__brand'],"count":k['productcount'],"denomination":k['brand__denomination'],'totalcost':totalcost}
                    product.append(data2)
            else:
                totalcost=0
                data2={"brand":j.brand,"count":0,"denomination":j.denomination,'totalcost':totalcost}
                product.append(data2)
        #print(topuser)
        list3=list()
        sorted_users = sorted(topuser, key=itemgetter('user'))

        for key, group in itertools.groupby(sorted_users, key=lambda x:x['user']):
            amountsum=0
            for g in group:
                amountsum=amountsum+g["amount"]
                #print(amountsum)
            data5={'user':key,'amount':amountsum}
            list3.append(data5)
        return render(request,"admin/dcard/dashboard-dcard.html",{'filterform':dcardDashboardfilter,'reseller':resellerlist,'recenttransactions':content,'products':product,'user':user,'topuser':list3,'last_month':last_month,'boxval':box_data})
    else:
        return redirect(LoginPage)

def filterdcardhomepage(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = dcardDashboardfilter(request.POST or None)
            print(form.errors)
            if form.is_valid():
                currentuser=request.session["user"]
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                usertype=form.cleaned_data.get("usertype")
                uuusername=form.cleaned_data.get("username")
                #mffromdate=datetime.strptime(fromdate, '%b %d %Y %I:%M%p')
                #print(type(fromdate))
                print(fromdate.strftime("%B %d, %Y"))
                last_month=fromdate.strftime("%B %d, %I:%M %p")+" To "+todate.strftime("%B %d, %I:%M %p")
                reseller = UserData.objects.filter(sponserId=currentuser,postId="Reseller")
                #print(reseller)
                resellerlist=list()
                for i in reseller:
                    resellerdata={'username':i.username,'name':i.name}
                    resellerlist.append(resellerdata)
                #print(username)
                userdetails = UserData.objects.get(username=request.session["user"])
                vcloudtxns = vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate,sponser1__username=currentuser,type="Dcard",sponser2__username=uuusername).order_by('-date')
                content=list()
                topuser=list()
                noofrecords=0
                productsum =0
                quantitysum =0
                profitsum =0
                count=0
                for i in vcloudtxns:
                    count=count+1
                    data={"id":i.id,"saleduser":i.sponser2.name,"role":i.sponser2.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(i.denominations*i.quantity),"profit":(i.margin1*i.quantity),"rtype":i.rtype}
                    data3={'user':i.sponser2.name,'amount':(i.denominations*i.quantity)}
                    topuser.append(data3)
                    content.append(data)
                    productsum=productsum+(i.denominations*i.quantity)
                    quantitysum=quantitysum+i.quantity
                    profitsum = profitsum+(i.margin1*i.quantity)
                box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum,'noofrecords':count}
                brand=vcloudBrands.objects.all()
                product=list()
                for j in brand:
                    prdcts=vcloudProducts.objects.filter(brand__id=j.id,status=True).order_by("brand__brand").values("brand").annotate(productcount=Count('brand')).values('brand__brand', 'productcount','brand__denomination')
                    #print(prdcts)
                    if(prdcts):
                        for k in prdcts:
                            totalcost=k['productcount']*k['brand__denomination']
                            data2={"brand":k['brand__brand'],"count":k['productcount'],"denomination":k['brand__denomination'],'totalcost':totalcost}
                            product.append(data2)
                    else:
                        totalcost=0
                        data2={"brand":j.brand,"count":0,"denomination":j.denomination,'totalcost':totalcost}
                        product.append(data2)
                #print(topuser)
                list3=list()
                sorted_users = sorted(topuser, key=itemgetter('user'))

                for key, group in itertools.groupby(sorted_users, key=lambda x:x['user']):
                    amountsum=0
                    for g in group:
                        amountsum=amountsum+g["amount"]
                        #print(amountsum)
                    data5={'user':key,'amount':amountsum}
                    list3.append(data5)
                return render(request,"admin/dcard/dashboard-dcard.html",{'filterform':vcloudDashboardfilter,'reseller':resellerlist,'recenttransactions':content,'products':product,'user':userdetails,'topuser':list3,'last_month':last_month,'boxval':box_data})
            else:
                return redirect(adminDcardDashboard)
        else:
            return(adminDcardDashboard)
    else:
        return redirect(LoginPage)

def dcardaddReseller(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"admin/dcard/addReseller.html",{'form':AddUserDataForm,'user':userdetails})
    else:
        return redirect(LoginPage)

def dcardaddUser(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"admin/dcard/addUser.html",{'form':AddUserDataForm,'user':userdetails})
    else:
        return redirect(LoginPage)

def dcardnewReseller(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = AddUserDataForm(request.POST or None)
            print(form.errors)
            if form.is_valid():
                username=form.cleaned_data.get("username")
                password=form.cleaned_data.get("password")
                hashkey = username+password
                hash = hashlib.sha256(hashkey.encode()).hexdigest()
                sponser = request.session["user"]
                sponseruser=UserData.objects.get(username=sponser)
                Userdata=form.save(commit=False)
                Userdata.postId="Reseller"
                Userdata.sponserId = sponseruser
                Userdata.status = True
                Userdata.balance = 0
                Userdata.targetAmt = 0
                Userdata.rentalAmt = 0
                Userdata.dcard_status = True
                Userdata.rcard_status = True
                Userdata.password = hash
                Userdata.save()
                messages.success(request, 'Successfully Added')
                return redirect(dcardaddReseller)
            else:
                userdetails = UserData.objects.get(username=request.session["user"])
                messages.warning(request, 'Internal Error Occured')
                form = AddUserDataForm()
                return render(request,"admin/dcard/addReseller.html",{'form':AddUserDataForm,'user':userdetails})
        else:
            userdetails = UserData.objects.get(username=request.session["user"])
            form = AddUserDataForm()
            return render(request,"admin/dcard/addReseller.html",{'form':AddUserDataForm,'user':userdetails})
    else:
        return redirect(LoginPage)

def dcardviewReseller(request):
    if request.session.has_key("user"):
        resellers = UserData.objects.filter(postId="Reseller")
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"admin/dcard/viewResellers.html",{'resellers':resellers,'user':userdetails})
    else:
        return redirect(LoginPage)

def dcardnewUser(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = AddUserDataForm(request.POST or None)
            print(form.errors)
            if form.is_valid():
                username=form.cleaned_data.get("username")
                password=form.cleaned_data.get("password")
                hashkey = username+password
                hash = hashlib.sha256(hashkey.encode()).hexdigest()
                sponser = request.session["user"]
                sponseruser=UserData.objects.get(username=sponser)
                Userdata=form.save(commit=False)
                Userdata.postId="User"
                Userdata.sponserId = sponseruser
                Userdata.status = True
                Userdata.balance = 0
                Userdata.targetAmt = 0
                Userdata.rentalAmt = 0
                Userdata.dcard_status = True
                Userdata.rcard_status = True
                Userdata.password = hash
                Userdata.save()
                messages.success(request, 'Successfully Added')
                return redirect(dcardaddUser)
            else:
                userdetails = UserData.objects.get(username=request.session["user"])
                messages.warning(request, form.errors)
                form = AddUserDataForm()
                return render(request,"admin/dcard/addUser.html",{'form':AddUserDataForm,'user':userdetails})
        else:
            userdetails = UserData.objects.get(username=request.session["user"])
            form = AddUserDataForm()
            return render(request,"admin/dcard/addUser.html",{'form':AddUserDataForm,'user':username})
    else:
        return redirect(LoginPage)

def dcardviewUser(request):
    if request.session.has_key("user"):
        user = request.session["user"]
        resellers = UserData.objects.filter(postId="User",sponserId=user)
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"admin/dcard/viewUser.html",{'resellers':resellers,'user':userdetails})
    else:
        return redirect(LoginPage)

def dcardprofile(request):
    if request.session.has_key("user"):
        user = request.session["user"]
        userDet = UserData.objects.get(username=user)
        return render(request,"admin/dcard/editProfile.html",{'user':userDet})
    else:
        return redirect(LoginPage)

def dcardeditProfile(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            user = request.session["user"]
            name = request.POST.get('name', None)
            address = request.POST.get('address', None)
            email = request.POST.get('email', None)
            mobileno = request.POST.get('mobileno', None)
            userDet = UserData.objects.get(username=user)
            userDet.name = name
            userDet.address = address
            userDet.email = email
            userDet.mobileno = mobileno
            userDet.save()
            messages.success(request, 'Successfully Updated')
            return redirect(dcardprofile)
        else:
            messages.warning(request,'Internal Error Occured')
            return redirect(dcardprofile)
    else:
        return redirect(LoginPage)

def dcardbalanceTransfer(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        bthist=balanceTransactionReport.objects.filter(source=userdetails,category="BT").order_by('-date')
        #print(bthist)
        return render(request,"admin/dcard/balanceTransfer.html",{'bthist':bthist,'user':userdetails})
    else:
        return redirect(LoginPage)

def dcardSubmitBalanceTransfer(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            userType = request.POST.get('userType', None)
            user = request.POST.get('users', None)
            amount = request.POST.get('amount', None)
            userdet = UserData.objects.get(username=user)
            bal = userdet.balance
            newbal=bal+Decimal(amount)
            cdbal = userdet.targetAmt
            newcdbal = cdbal-Decimal(amount)
            userdet.targetAmt = newcdbal
            userdet.balance = newbal
            userdet.save()
            userdetails = UserData.objects.get(username=request.session["user"])
            btreport = balanceTransactionReport()
            btreport.source = userdetails
            btreport.destination = userdet
            btreport.category = "BT"
            btreport.amount = amount
            btreport.pbalance = bal
            btreport.nbalance = newbal
            btreport.cramount = newcdbal
            btreport.remarks = 'Added To Balance'
            btreport.save()
            messages.success(request, 'Successfully Updated The balance')
            return redirect(dcardbalanceTransfer)
            #userdata=UserData.objects.get(username=)
        else:
            messages.warning(request, 'Internal Error Occured')
            return redirect(dcardbalanceTransfer)
    else:
        return redirect(LoginPage)

def dcardaddPayment(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        phist=fundTransactionReport.objects.filter(source=userdetails).order_by('-date')
        return render(request,"admin/dcard/addPayment.html",{'phist':phist})
    else:
        return redirect(LoginPage)

def dcardsubmitPayment(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            userType = request.POST.get('userType', None)
            user = request.POST.get('users', None)
            amount = request.POST.get('amount', None)
            remarks = request.POST.get('remarks', None)
            userdet = UserData.objects.get(username=user)
            obalance =userdet.targetAmt
            cdbal = userdet.targetAmt
            newcdbal = cdbal+Decimal(amount)
            userdet.targetAmt = newcdbal
            userdet.save()
            closeuser = UserData.objects.get(username=user)
            userdetails = UserData.objects.get(username=request.session["user"])
            ftreport=fundTransactionReport()
            ftreport.source = userdetails
            ftreport.destination = userdet
            ftreport.obalance = obalance
            ftreport.cbalance = closeuser.targetAmt
            ftreport.role = userType
            ftreport.amount = amount
            ftreport.balance = newcdbal
            ftreport.remarks = remarks
            ftreport.save()
            messages.success(request, 'Successfully Updated The balance')
            return redirect(dcardaddPayment)
        else:
            messages.warning(request, 'Internal Error Occured')
            return redirect(dcardaddPayment)
    else:
        return redirect(LoginPage)

def dcardbalanceTransferReport(request):
    if request.session.has_key("user"):
        username = request.session["user"]
        userdetails = UserData.objects.get(username=request.session["user"])
        reseller = UserData.objects.filter(sponserId=username,postId="Reseller")
        sum = balanceTransactionReport.objects.filter(source=userdetails,category='BT').aggregate(Sum('amount'))
        bthist = balanceTransactionReport.objects.filter(source=userdetails).order_by('-date')
        return render(request,"admin/dcard/balanceTransferReport.html",{'form':balancetransferfilterform,'reseller':reseller,'bthist':bthist,'sum':sum['amount__sum'],'user':userdetails})
    else:
        return redirect(LoginPage)

def filterdcardbtreport(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            form = balancetransferfilterform(request.POST or None)
            print(form.errors)
            if form.is_valid():
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                usertype=form.cleaned_data.get("usertype")
                susername=form.cleaned_data.get("username")
                username = request.session["user"]
                filter={'ffdate':fromdate,'ttdate':todate,'fuser':susername}
                userdetails = UserData.objects.get(username=request.session["user"])
                reseller = UserData.objects.filter(sponserId=username,postId="Reseller")
                sum=list()
                bthist=None
                try:
                    if(usertype == "All" and susername == "All"):
                        sum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails).aggregate(Sum('amount'))
                        bthist = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails)
                    elif(usertype!="All" and susername == "All"):
                        sum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails, destination__postId=usertype).aggregate(Sum('amount'))
                        bthist = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails, destination__postId=usertype)
                    else:
                        sum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__username=susername).aggregate(Sum('amount'))
                        bthist = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__username=susername)
                except:
                    pass
                return render(request,"admin/dcard/balanceTransferReport.html",{'form':balancetransferfilterform,'reseller':reseller,'bthist':bthist,'sum':sum['amount__sum'],'user':userdetails,'filter':filter})
            else:
                return redirect(dcardbalanceTransferReport)
        else:
            return redirect(dcardbalanceTransferReport)
    else:
        return redirect(LoginPage)

def dcardpaymentReport(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        reseller = UserData.objects.filter(sponserId=request.session["user"],postId="Reseller")
        phist = fundTransactionReport.objects.filter(source=userdetails).order_by('-date')
        bsum = fundTransactionReport.objects.filter(source=userdetails).aggregate(Sum('amount'))
        return render(request,"admin/dcard/paymentReport.html",{'form':paymentfilterform,'reseller':reseller,'phist':phist,'sum':bsum['amount__sum'],'user':userdetails})
    else:
        return redirect(LoginPage)

def filterdcardpaymentreport(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            form = balancetransferfilterform(request.POST or None)
            print(form.errors)
            if form.is_valid():
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                usertype=form.cleaned_data.get("usertype")
                susername=form.cleaned_data.get("username")
                username = request.session["user"]
                filter={'ffdate':fromdate,'ttdate':todate,'fuser':susername}
                userdetails = UserData.objects.get(username=request.session["user"])
                reseller = UserData.objects.filter(sponserId=username,postId="Reseller")
                sum=None
                bthist=None
                try:
                    if(usertype == "All" and susername == "All"):
                        bsum = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails).aggregate(Sum('amount'))
                        phist = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails)
                    elif(usertype!="All" and susername == "All"):
                        bsum = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails, destination__postId=usertype).aggregate(Sum('amount'))
                        phist = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails, destination__postId=usertype)
                    else:
                        bsum = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__username=susername).aggregate(Sum('amount'))
                        phist = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__username=susername)
                except:
                    pass
                return render(request,"admin/dcard/paymentReport.html",{'form':paymentfilterform,'reseller':reseller,'phist':phist,'sum':bsum['amount__sum'],'user':userdetails,'filter':filter})
            else:
                return redirect(dcardpaymentReport)
        else:
            return redirect(dcardpaymentReport)
    else:
        return redirect(LoginPage)

def addDCardBrand(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"admin/dcard/adddcardbrand.html",{'form':AddDCardBrands,'user':userdetails})
    else:
        return redirect(LoginPage)

def submitDCardBrands(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = AddDCardBrands(request.POST, request.FILES)
            #print(form.errors)
            if form.is_valid():
                branddata=form.save()
                messages.success(request, 'Successfully Added The Brands')
                return redirect(addDCardBrand)
            else:
                messages.warning(request, 'Internal Error Occured')
                return redirect(addDCardBrand)
        else:
            return redirect(addDCardBrand)
    else:
        return redirect(LoginPage)

def manageDCardBrands(request):
    if request.session.has_key("user"):
        brands = dcardBrands.objects.all()
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"admin/dcard/managedcardbrand.html",{'brands':brands,'user':userdetails})
    else:
        return redirect(LoginPage)

def assignDCardBrands(request):
    if request.session.has_key("user"):
        brands=dcardBrands.objects.all()
        #brands = datacardproducts.objects.filter(status=True).order_by('brand').values('brand').annotate(count=Count('brand')).values('brand__id','brand__brand','brand__denomination','count','brand__description','brand__logo','brand__currency')
        print(brands)
        resellers = UserData.objects.filter(postId="Reseller")
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"admin/dcard/assignDcardbrand.html",{'brands':brands,'resellers':resellers,'user':userdetails})
    else:
        return redirect(LoginPage)

def getDCardBrandDetails(request):
    id = request.GET.get('id', None)
    brdet = dcardBrands.objects.get(id=id)
    data={"id":brdet.id,"brand":brdet.brand,"logo":brdet.logo.url,"rate":brdet.denomination,"desc":brdet.description}
    #print(data)
    return JsonResponse(data)

def submitDcardManageBrands(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = editDcardBrands(request.POST, request.FILES)
            if form.is_valid():
                id = form.cleaned_data.get("id")
                brandname = form.cleaned_data.get("brand")
                flag=True;
                brand = dcardBrands.objects.get(id=id)
                try:
                    logo = request.FILES['logo']
                    brand.logo = logo
                    print(logo)
                except:
                    flag=False;
                description = form.cleaned_data.get("desc")
                denomination = form.cleaned_data.get("rate")
                brand.brand = brandname
                brand.description = description
                brand.denomination = denomination
                brand.save()
                print(brand)
                return redirect(manageDCardBrands)
            else:
                print(form.errors)
                return redirect(manageDCardBrands)
        else:
            return redirect(manageDCardBrands)
    else:
        return redirect(LoginPage)

def adddcardProduct(request):
    if request.session.has_key("user"):
        choices=dcardBrands.objects.all().values('id', 'brand')
        print(choices)
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"admin/dcard/addDcardProduct.html",{'productform':AddDcardProducts,'brandform':AddDCardBrands,'choices':choices,'user':userdetails})
    else:
        return redirect(LoginPage)

def submitdcardProducts(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            try:
                form = AddDcardProducts(request.POST or None)
                if form.is_valid():
                    brandid = form.cleaned_data.get("brand")
                    username = form.cleaned_data.get("username")
                    res=datacardproducts.objects.filter(username = username).exists()
                    print(res)
                    res1=dcardupproducts.objects.filter(username = username).exists()
                    print(res1)
                    if(res or res1):
                        messages.warning(request, 'Product is alreday updated in Csv log. Go and spent the product')
                    else:
                        product = datacardproducts()
                        branddet = dcardBrands.objects.get(id=brandid)
                        product.brand = branddet
                        product.username = username
                        product.denomination = branddet.denomination
                        product.save()
                        messages.success(request, 'Successfully Added The Products')
                    return redirect(adddcardProduct)
                else:
                    messages.warning(request, form.errors)
                    return redirect(adddcardProduct)
            except:
                return redirect(adddcardProduct)
        else:
            return redirect(adddcardProduct)
    else:
        return redirect(LoginPage)


def dcardmanageProduct(request):
    if request.session.has_key("user"):
        product = datacardproducts.objects.all().order_by('-cdate')[:5000]
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"admin/dcard/manageProduct.html",{'products':product,'user':userdetails})
    else:
        return redirect(LoginPage)

def saveassignDCardBrands(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            try:
                reseller = request.POST.get('username', None)
                values = request.POST.get('values', None)
                states = request.POST.get('states', None)
                brands = request.POST.get('brands', None)
                margins = request.POST.get('margins', None)
                v = values.split(',')
                s = states.split(',')
                b = brands.split(',')
                m = margins.split(',')
                username = request.session["user"]
                assignedby = UserData.objects.get(username=username)
                assignedto = UserData.objects.get(username=reseller)
                for i in range(0,len(s)):
                    if(int(s[i])==0):
                        print(True)
                        brandid=b[int(i)]
                        brdet=dcardBrands.objects.get(id=brandid)
                        print(brdet)
                        try:
                            vdt = datacardAssignments.objects.get(brand=brdet,assignedby=assignedby,assignedto=assignedto)
                            vdt.delete()
                            vadt = datacardAssignments.objects.filter(brand=brdet,assignedby=assignedto)
                            print(vadt)
                            for j in vadt:
                                try:
                                    ud = datacardAssignments.objects.filter(brand=brdet,assignedby=j.assignedto)
                                    print(ud)
                                    ud.delete()
                                except Exception as e:
                                    print(e)
                                    pass;
                            #print(vadt)
                            vadt.delete()
                        except Exception as e:
                            print (e)
                            print("Error")
                    else:
                        print(False)
                        brandid=b[int(i)]
                        brdet=dcardBrands.objects.get(id=brandid)
                        try:
                            assdet = datacardAssignments.objects.get(brand=brdet,assignedby=assignedby,assignedto=assignedto)
                            assdet.margin = Decimal(v[int(i)])
                            assdet.save()
                        except datacardAssignments.DoesNotExist:
                            vass = datacardAssignments()
                            vass.brand=brdet
                            vass.assignedto=assignedto
                            vass.assignedby=assignedby
                            vass.margin = Decimal(v[int(i)])
                            vass.save()
                data={"status":"Success"}
                return JsonResponse(data)
            except Exception as e:
                print(e)
                return JsonResponse({"status":"Error"})
        else:
            pass
    else:
        return redirect(LoginPage)

def dcardstore(request):
    if request.session.has_key("user"):
        ads = adverisements.objects.filter(adtype="Image",ctype="Dcard").order_by('-id')[:10]
        dcardproducts = datacardproducts.objects.filter(status=True).order_by('brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
        some_list = []
        data = dict()
        for i in dcardproducts:
            brandname=i["brand__brand"]
            bd=brandname.split(' ')
            bname=bd[0]
            print(bname)
            if any(bname in s for s in some_list):
                pass
            else:
                some_list.append(bname)
        totalfil=len(some_list)
        print(totalfil)
        if(totalfil!=0):
            classlist=[]
            for j in range(0,totalfil):
                if(j==0):
                    classlist.append("btn-warning")
                else:
                    classlist.append("btn-success")
                btnlist = zip(some_list, classlist)
                print(btnlist)
                userdetails = UserData.objects.get(username=request.session["user"])
                item=datacardproducts.objects.filter(status=True,brand__brand__contains=some_list[0]).order_by('brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
        else:
            item=None
            btnlist=None
            userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"admin/dcard/datastore.html",{'dcardproducts':item,'btnlist':btnlist,'user':userdetails,'ads':ads})
    else:
        return redirect(LoginPage)


def filtereddatastore(request,brand):
    if request.session.has_key("user"):
        ads = adverisements.objects.filter(adtype="Image",ctype="Dcard").order_by('-id')[:10]
        dcardproducts = datacardproducts.objects.filter(status=True).order_by('brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
        some_list = []
        data = dict()
        for i in dcardproducts:
            brandname=i["brand__brand"]
            bd=brandname.split(' ')
            bname=bd[0]
            #print(bname)
            if any(bname in s for s in some_list):
                pass
            else:
                some_list.append(bname)
        totalfil=len(some_list)
        position=0
        for index, inbrand in enumerate(some_list):
            print(inbrand)
            #print(bname)
            if inbrand == brand:
                position=index
                print(position)
        classlist=[]
        for j in range(0,totalfil):
            if(j==position):
                classlist.append("btn-warning")
            else:
                classlist.append("btn-success")
        print(classlist)
        btnlist = zip(some_list, classlist)
        #print(btnlist)
        item=datacardproducts.objects.filter(status=True,brand__brand__contains=brand).order_by('brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"admin/dcard/datastore.html",{'dcardproducts':item,'btnlist':btnlist,'totalfil':totalfil,'user':userdetails,'ads':ads})
    else:
        return redirect(LoginPage)

def datacardreport(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        username=request.session["user"]
        last_month = datetime.today() - timedelta(days=1)
        vcloudtxns = vcloudtransactions.objects.filter(date__gte=last_month,sponser1__username=username).order_by('-date')
        #vcloudtxns = vcloudtransactions.objects.all().order_by('-date')
        reseller=UserData.objects.filter(sponserId=username,postId="Reseller")
        resellerlist=list()
        vcbrand=vcloudBrands.objects.all()
        vcbrandlist=list()
        for b in vcbrand:
            branddata={'brand':b.brand}
            vcbrandlist.append(branddata)

        for i in reseller:
            resellerdata={'username':i.username,'name':i.name}
            resellerlist.append(resellerdata)
        content=list()
        noofrecords=0
        productsum =0
        quantitysum =0
        profitsum =0
        for i in vcloudtxns:
            data={"id":i.id,"saleduser":i.sponser2.name,"role":i.sponser2.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(i.denominations*i.quantity),"profit":(i.margin1*i.quantity),"rtype":i.rtype}
            content.append(data)
            productsum=productsum+(i.denominations*i.quantity)
            quantitysum=quantitysum+i.quantity
            profitsum = profitsum+(i.margin1*i.quantity)
        box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum}
        return render(request,"admin/dcard/dcardreport.html",{'filterform':vcloudreportfilterform,'products':content,'user':userdetails,'reseller':resellerlist, 'brand':vcbrandlist,'box':box_data,'date':last_month})
    else:
        return redirect(LoginPage)

def filterdcard_report(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            form = vcloudreportfilterform(request.POST or None)
            print(form.errors)
            if form.is_valid():
                username=request.session["user"]
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                usertype=form.cleaned_data.get("usertype")
                print(usertype)
                fusername=form.cleaned_data.get("username")
                type=form.cleaned_data.get("type")
                brand=form.cleaned_data.get("brand")
                userdetails = UserData.objects.get(username=request.session["user"])
                fuser=''
                if(fusername!='All'):
                    filterdata=UserData.objects.get(username=fusername)
                    fuser=filterdata.name
                else:
                    fuser=fusername
                filter={'ffdate':fromdate,'ttdate':todate,'fuser':fuser}
                reseller=UserData.objects.filter(sponserId=username,postId="Reseller")
                resellerlist=list()
                vcbrand=vcloudBrands.objects.all()
                vcbrandlist=list()
                for b in vcbrand:
                    branddata={'brand':b.brand}
                    vcbrandlist.append(branddata)

                for i in reseller:
                    resellerdata={'username':i.username,'name':i.name}
                    resellerlist.append(resellerdata)

                content=list()
                noofrecords = 0
                productsum = 0
                quantitysum = 0
                profitsum = 0
                vcloudtxns=vcloudtransactions()
                try:
                    print(usertype)
                    print(fusername)
                    print(type)
                    print(brand)
                    if(usertype=="All" and fusername=="All" and type=="All" and brand=="All"):
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser1__username=username).order_by('-date')
                        print("One")
                    elif(usertype=="All" and fusername=="All" and type=="All" and brand !="All"):
                        print("TWo")
                        vcloudtxns==vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser1__username=username, brand=brand).order_by('-date')
                    elif(usertype=="All" and fusername=="All" and type !="All" and brand =="All"):
                        print("Three")
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser1__username=username, type=type).order_by('-date')
                    elif(usertype=="All" and fusername=="All" and type !="All" and brand !="All"):
                        print("four")
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser1__username=username, brand=brand).order_by('-date')
                    elif(usertype=="All" and fusername!="All" and type !="All" and brand !="All"):
                        print('five')
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, type=type, sponser1__username=username, sponser2__username=fusername, brand=brand).order_by('-date')
                    elif(usertype !="All" and fusername =="All" and type =="All" and brand !="All"):
                        print('Six')
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser2__type=usertype, sponser1__username=username).order_by('-date')
                    elif(usertype !="All" and fusername =="All" and type =="All" and brand =="All"):
                        print('Six')
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser1__username=username, sponser2__postId=usertype).order_by('-date')
                    elif(usertype =="All" and fusername !="All" and type =="All" and brand =="All"):
                        print('Six')
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser1__username=username, sponser2__username=fusername).order_by('-date')
                    elif(usertype !="All" and fusername !="All" and type =="All" and brand =="All"):
                        print('Six')
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser1__username=username, sponser2__username=fusername).order_by('-date')
                    else:
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser1__username=username, sponser2__username=fusername,brand=brand).order_by('-date')
                    print(vcloudtxns)
                    for i in vcloudtxns:
                        data={"id":i.id,"saleduser":i.sponser2.name,"role":i.sponser2.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(i.denominations*i.quantity),"profit":(i.margin1*i.quantity),"rtype":i.rtype}
                        content.append(data)
                        productsum=productsum+(i.denominations*i.quantity)
                        quantitysum=quantitysum+i.quantity
                        profitsum = profitsum+(i.margin1*i.quantity)
                except:
                    pass
                box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum}
                return render(request,"admin/dcard/dcardreport.html",{'filterform':vcloudreportfilterform,'products':content,'user':userdetails,'reseller':resellerlist, 'brand':vcbrandlist,'box':box_data,'filter':filter})
            else:
                return redirect(dcardreport)
        else:
            return redirect(dcardreport)
    else:
        return redirect(LoginPage)

#________________RCARD_______________

def adminRcardDashboard(request):
    if request.session.has_key("user"):
        last_month = datetime.today() - timedelta(days=1)
        username = request.session["user"]
        reseller = UserData.objects.filter(sponserId=username,postId="Reseller")
        resellerlist=list()
        for i in reseller:
            resellerdata={'username':i.username,'name':i.name}
            resellerlist.append(resellerdata)
        #print(list(reseller[0]))
        type = request.session["usertype"]
        try:
            user = UserData.objects.get(username = username, postId = type)
        except UserData.DoesNotExist:
            return redirect(LoginPage)
        userdetails = UserData.objects.get(username=request.session["user"])
        username=request.session["user"]
        last_month = datetime.today() - timedelta(days=1)
        vcloudtxns = vcloudtransactions.objects.filter(date__gte=last_month,sponser1__username=username,type="Rcard").order_by('-date')
        content=list()
        topuser=list()
        noofrecords=0
        productsum =0
        quantitysum =0
        profitsum =0
        count=0
        for i in vcloudtxns:
            count=count+1
            data={"id":i.id,"saleduser":i.sponser2.name,"role":i.sponser2.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(i.denominations*i.quantity),"profit":(i.margin1*i.quantity),"rtype":i.rtype}
            data3={'user':i.sponser2.name,'amount':(i.denominations*i.quantity)}
            topuser.append(data3)
            content.append(data)
            productsum=productsum+(i.denominations*i.quantity)
            quantitysum=quantitysum+i.quantity
            profitsum = profitsum+(i.margin1*i.quantity)
        box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum,'noofrecords':count}
        brand=rcardBrands.objects.all()
        product=list()
        for j in brand:
            prdcts=rcardProducts.objects.filter(brand__id=j.id,status=True).order_by("brand__brand").values("brand").annotate(productcount=Count('brand')).values('brand__brand', 'productcount','brand__denomination')
            #print(prdcts)
            if(prdcts):
                for k in prdcts:
                    totalcost=k['productcount']*k['brand__denomination']
                    data2={"brand":k['brand__brand'],"count":k['productcount'],"denomination":k['brand__denomination'],"totalcost":totalcost}
                    product.append(data2)
            else:
                totalcost=0
                data2={"brand":j.brand,"count":0,"denomination":j.denomination,"totalcost":totalcost}
                product.append(data2)
        #print(topuser)
        list3=list()
        sorted_users = sorted(topuser, key=itemgetter('user'))

        for key, group in itertools.groupby(sorted_users, key=lambda x:x['user']):
            amountsum=0
            for g in group:
                amountsum=amountsum+g["amount"]
                #print(amountsum)
            data5={'user':key,'amount':amountsum}
            list3.append(data5)
        return render(request,"admin/rcard/dashboard-rcard.html",{'filterform':rcardDashboardfilter,'reseller':resellerlist,'recenttransactions':content,'products':product,'user':user,'topuser':list3,'last_month':last_month,'boxval':box_data})
    else:
        return redirect(LoginPage)

def filterrcardhomepage(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = rcardDashboardfilter(request.POST or None)
            print(form.errors)
            if form.is_valid():
                currentuser=request.session["user"]
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                usertype=form.cleaned_data.get("usertype")
                uuusername=form.cleaned_data.get("username")
                #mffromdate=datetime.strptime(fromdate, '%b %d %Y %I:%M%p')
                #print(type(fromdate))
                print(fromdate.strftime("%B %d, %Y"))
                last_month=fromdate.strftime("%B %d, %I:%M %p")+" To "+todate.strftime("%B %d, %I:%M %p")
                reseller = UserData.objects.filter(sponserId=currentuser,postId="Reseller")
                #print(reseller)
                resellerlist=list()
                for i in reseller:
                    resellerdata={'username':i.username,'name':i.name}
                    resellerlist.append(resellerdata)
                #print(username)
                userdetails = UserData.objects.get(username=request.session["user"])
                vcloudtxns = vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate,sponser1__username=currentuser,type="Vcloud",sponser2__username=uuusername).order_by('-date')
                content=list()
                topuser=list()
                noofrecords=0
                productsum =0
                quantitysum =0
                profitsum =0
                count=0
                for i in vcloudtxns:
                    count=count+1
                    data={"id":i.id,"saleduser":i.sponser2.name,"role":i.sponser2.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(i.denominations*i.quantity),"profit":(i.margin1*i.quantity),"rtype":i.rtype}
                    data3={'user':i.sponser2.name,'amount':(i.denominations*i.quantity)}
                    topuser.append(data3)
                    content.append(data)
                    productsum=productsum+(i.denominations*i.quantity)
                    quantitysum=quantitysum+i.quantity
                    profitsum = profitsum+(i.margin1*i.quantity)
                box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum,'noofrecords':count}
                brand=rcardBrands.objects.all()
                product=list()
                for j in brand:
                    prdcts=rcardProducts.objects.filter(brand__id=j.id,status=True).order_by("brand__brand").values("brand").annotate(productcount=Count('brand')).values('brand__brand', 'productcount','brand__denomination')
                    if(prdcts):
                        for k in prdcts:
                            totalcost=k['productcount']*k['brand__denomination']
                            data2={"brand":k['brand__brand'],"count":k['productcount'],"denomination":k['brand__denomination'],"totalcost":totalcost}
                            product.append(data2)
                    else:
                        totalcost=0
                        data2={"brand":j.brand,"count":0,"denomination":j.denomination,"totalcost":totalcost}
                        product.append(data2)
                #print(topuser)
                list3=list()
                sorted_users = sorted(topuser, key=itemgetter('user'))

                for key, group in itertools.groupby(sorted_users, key=lambda x:x['user']):
                    amountsum=0
                    for g in group:
                        amountsum=amountsum+g["amount"]
                        #print(amountsum)
                    data5={'user':key,'amount':amountsum}
                    list3.append(data5)
                return render(request,"admin/rcard/dashboard-rcard.html",{'filterform':rcardDashboardfilter,'reseller':resellerlist,'recenttransactions':content,'products':product,'user':userdetails,'topuser':list3,'last_month':last_month,'boxval':box_data})
            else:
                return redirect(adminRcardDashboard)
        else:
            return(adminRcardDashboard)
    else:
        return redirect(LoginPage)

def rcardaddReseller(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"admin/rcard/addReseller.html",{'form':AddUserDataForm,'user':userdetails})
    else:
        return redirect(LoginPage)

def rcardaddUser(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"admin/rcard/addUser.html",{'form':AddUserDataForm,'user':userdetails})
    else:
        return redirect(LoginPage)

def getRCardBrandDetails(request):
    id = request.GET.get('id', None)
    brdet = rcardBrands.objects.get(id=id)
    data={"id":brdet.id,"brand":brdet.brand,"logo":brdet.logo.url,"rate":brdet.denomination,"desc":brdet.description}
    #print(data)
    return JsonResponse(data)

def submitRcardManageBrands(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = editRcardBrands(request.POST, request.FILES)
            if form.is_valid():
                id = form.cleaned_data.get("id")
                brandname = form.cleaned_data.get("brand")
                flag=True;
                brand = rcardBrands.objects.get(id=id)
                try:
                    logo = request.FILES['logo']
                    brand.logo = logo
                    print(logo)
                except:
                    flag=False;
                description = form.cleaned_data.get("desc")
                denomination = form.cleaned_data.get("rate")
                brand.brand = brandname
                brand.description = description
                brand.denomination = denomination
                brand.save()
                print(brand)
                return redirect(manageRCardBrands)
            else:
                print(form.errors)
                return redirect(manageRCardBrands)
        else:
            return redirect(manageRCardBrands)
    else:
        return redirect(LoginPage)

def rcardnewReseller(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = AddUserDataForm(request.POST or None)
            print(form.errors)
            if form.is_valid():
                username=form.cleaned_data.get("username")
                password=form.cleaned_data.get("password")
                hashkey = username+password
                hash = hashlib.sha256(hashkey.encode()).hexdigest()
                sponser = request.session["user"]
                sponseruser=UserData.objects.get(username=sponser)
                Userdata=form.save(commit=False)
                Userdata.postId="Reseller"
                Userdata.sponserId = sponseruser
                Userdata.status = True
                Userdata.balance = 0
                Userdata.targetAmt = 0
                Userdata.rentalAmt = 0
                Userdata.dcard_status = True
                Userdata.rcard_status = True
                Userdata.password = hash
                Userdata.save()
                messages.success(request, 'Successfully Added')
                return redirect(rcardaddReseller)
            else:
                userdetails = UserData.objects.get(username=request.session["user"])
                messages.warning(request, 'Internal Error Occured')
                form = AddUserDataForm()
                return render(request,"admin/rcard/addReseller.html",{'form':AddUserDataForm,'user':userdetails})
        else:
            userdetails = UserData.objects.get(username=request.session["user"])
            form = AddUserDataForm()
            return render(request,"admin/rcard/addReseller.html",{'form':AddUserDataForm,'user':userdetails})
    else:
        return redirect(LoginPage)

def rcardviewReseller(request):
    if request.session.has_key("user"):
        resellers = UserData.objects.filter(postId="Reseller")
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"admin/rcard/viewResellers.html",{'resellers':resellers,'user':userdetails})
    else:
        return redirect(LoginPage)

def rcardnewUser(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = AddUserDataForm(request.POST or None)
            print(form.errors)
            if form.is_valid():
                username=form.cleaned_data.get("username")
                password=form.cleaned_data.get("password")
                hashkey = username+password
                hash = hashlib.sha256(hashkey.encode()).hexdigest()
                sponser = request.session["user"]
                sponseruser=UserData.objects.get(username=sponser)
                Userdata=form.save(commit=False)
                Userdata.postId="User"
                Userdata.sponserId = sponseruser
                Userdata.status = True
                Userdata.balance = 0
                Userdata.targetAmt = 0
                Userdata.rentalAmt = 0
                Userdata.dcard_status = True
                Userdata.rcard_status = True
                Userdata.password = hash
                Userdata.save()
                messages.success(request, 'Successfully Added')
                return redirect(rcardaddUser)
            else:
                userdetails = UserData.objects.get(username=request.session["user"])
                messages.warning(request, 'Internal Error Occured')
                form = AddUserDataForm()
                return render(request,"admin/rcard/addUser.html",{'form':AddUserDataForm,'user':userdetails})
        else:
            userdetails = UserData.objects.get(username=request.session["user"])
            form = AddUserDataForm()
            return render(request,"admin/rcard/addUser.html",{'form':AddUserDataForm,'user':userdetails})
    else:
        return redirect(LoginPage)

def rcardviewUser(request):
    if request.session.has_key("user"):
        user = request.session["user"]
        userdetails = UserData.objects.get(username=request.session["user"])
        resellers = UserData.objects.filter(postId="User",sponserId=user)
        return render(request,"admin/rcard/viewUser.html",{'resellers':resellers,'user':userdetails})
    else:
        return redirect(LoginPage)

def rcardprofile(request):
    if request.session.has_key("user"):
        user = request.session["user"]
        userDet = UserData.objects.get(username=user)
        return render(request,"admin/rcard/editProfile.html",{'user':userDet})
    else:
        return redirect(LoginPage)

def rcardeditProfile(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            user = request.session["user"]
            name = request.POST.get('name', None)
            address = request.POST.get('address', None)
            email = request.POST.get('email', None)
            mobileno = request.POST.get('mobileno', None)
            userDet = UserData.objects.get(username=user)
            userDet.name = name
            userDet.address = address
            userDet.email = email
            userDet.mobileno = mobileno
            userDet.save()
            messages.success(request, 'Successfully Updated')
            return redirect(rcardprofile)
        else:
            messages.warning(request,'Internal Error Occured')
            return redirect(rcardprofile)
    else:
        return redirect(LoginPage)

def rcardbalanceTransfer(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        bthist=balanceTransactionReport.objects.filter(source=userdetails,category="BT").order_by('-date')
        #print(bthist)
        return render(request,"admin/rcard/balanceTransfer.html",{'bthist':bthist,'user':userdetails})
    else:
        return redirect(LoginPage)

def rcardSubmitBalanceTransfer(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            userType = request.POST.get('userType', None)
            user = request.POST.get('users', None)
            amount = request.POST.get('amount', None)
            userdet = UserData.objects.get(username=user)
            bal = userdet.balance
            newbal=bal+Decimal(amount)
            cdbal = userdet.targetAmt
            newcdbal = cdbal-Decimal(amount)
            userdet.targetAmt = newcdbal
            userdet.balance = newbal
            userdet.save()
            userdetails = UserData.objects.get(username=request.session["user"])
            btreport = balanceTransactionReport()
            btreport.source = userdetails
            btreport.destination = userdet
            btreport.category = "BT"
            btreport.amount = amount
            btreport.pbalance = bal
            btreport.nbalance = newbal
            btreport.cramount = newcdbal
            btreport.remarks = 'Added To Balance'
            btreport.save()
            messages.success(request, 'Successfully Updated The balance')
            return redirect(rcardbalanceTransfer)
            #userdata=UserData.objects.get(username=)
        else:
            messages.warning(request, 'Internal Error Occured')
            return redirect(rcardbalanceTransfer)
    else:
        return redirect(LoginPage)

def rcardaddPayment(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        phist=fundTransactionReport.objects.filter(source=userdetails).order_by('-date')
        return render(request,"admin/rcard/addPayment.html",{'phist':phist,'user':userdetails})
    else:
        return redirect(LoginPage)

def rcardsubmitPayment(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            userType = request.POST.get('userType', None)
            user = request.POST.get('users', None)
            amount = request.POST.get('amount', None)
            remarks = request.POST.get('remarks', None)
            userdet = UserData.objects.get(username=user)
            obalance = userdet.targetAmt
            cdbal = userdet.targetAmt
            newcdbal = cdbal+Decimal(amount)
            userdet.targetAmt = newcdbal
            userdet.save()
            closeuser = UserData.objects.get(username=user)
            userdetails = UserData.objects.get(username=request.session["user"])
            ftreport=fundTransactionReport()
            ftreport.source = userdetails
            ftreport.destination = userdet
            ftreport.obalance = obalance
            ftreport.cbalance = closeuser.targetAmt
            ftreport.role = userType
            ftreport.amount = amount
            ftreport.balance = newcdbal
            ftreport.remarks = remarks
            ftreport.save()
            messages.success(request, 'Successfully Updated The balance')
            return redirect(rcardaddPayment)
        else:
            messages.warning(request, 'Internal Error Occured')
            return redirect(rcardaddPayment)
    else:
        return redirect(LoginPage)

def rcardbalanceTransferReport(request):
    if request.session.has_key("user"):
        username = request.session["user"]
        userdetails = UserData.objects.get(username=request.session["user"])
        reseller = UserData.objects.filter(sponserId=username,postId="Reseller")
        sum = balanceTransactionReport.objects.filter(source=userdetails,category='BT').aggregate(Sum('amount'))
        bthist = balanceTransactionReport.objects.filter(source=userdetails).order_by('-date')
        return render(request,"admin/rcard/balanceTransferReport.html",{'form':balancetransferfilterform,'reseller':reseller,'bthist':bthist,'sum':sum['amount__sum'],'user':userdetails})
    else:
        return redirect(LoginPage)

def filterrcardbtreport(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            form = balancetransferfilterform(request.POST or None)
            print(form.errors)
            if form.is_valid():
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                usertype=form.cleaned_data.get("usertype")
                susername=form.cleaned_data.get("username")
                username = request.session["user"]
                #fuser=UserData.objects.get(username=susername)
                filter={'ffdate':fromdate,'ttdate':todate,'fuser':susername}
                userdetails = UserData.objects.get(username=request.session["user"])
                reseller = UserData.objects.filter(sponserId=username,postId="Reseller")
                sum=list()
                bthist=None
                try:
                    if(usertype == "All" and susername == "All"):
                        sum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails).aggregate(Sum('amount'))
                        bthist = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails)
                    elif(usertype!="All" and susername == "All"):
                        sum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails, destination__postId=usertype).aggregate(Sum('amount'))
                        bthist = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails, destination__postId=usertype)
                    else:
                        sum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__username=susername).aggregate(Sum('amount'))
                        bthist = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__username=susername)
                except:
                    pass
                return render(request,"admin/rcard/balanceTransferReport.html",{'form':balancetransferfilterform,'reseller':reseller,'bthist':bthist,'sum':sum['amount__sum'],'user':userdetails,'filter':filter})
            else:
                return redirect(rcardbalanceTransferReport)
        else:
            return redirect(rcardbalanceTransferReport)
    else:
        return redirect(LoginPage)

def rcardpaymentReport(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        reseller = UserData.objects.filter(sponserId=request.session["user"],postId="Reseller")
        phist = fundTransactionReport.objects.filter(source=userdetails).order_by('-date')
        bsum = fundTransactionReport.objects.filter(source=userdetails).aggregate(Sum('amount'))
        return render(request,"admin/rcard/paymentReport.html",{'form':paymentfilterform,'reseller':reseller,'phist':phist,'sum':bsum['amount__sum'],'user':userdetails})
    else:
        return redirect(LoginPage)

def filterrcardpaymentreport(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            form = balancetransferfilterform(request.POST or None)
            print(form.errors)
            if form.is_valid():
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                usertype=form.cleaned_data.get("usertype")
                susername=form.cleaned_data.get("username")
                username = request.session["user"]
                filter={'ffdate':fromdate,'ttdate':todate,'fuser':susername}
                userdetails = UserData.objects.get(username=request.session["user"])
                reseller = UserData.objects.filter(sponserId=username,postId="Reseller")
                sum=None
                bthist=None
                try:
                    if(usertype == "All" and susername == "All"):
                        bsum = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails).aggregate(Sum('amount'))
                        phist = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails)
                    elif(usertype!="All" and susername == "All"):
                        bsum = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails, destination__postId=usertype).aggregate(Sum('amount'))
                        phist = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails, destination__postId=usertype)
                    else:
                        bsum = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__username=susername).aggregate(Sum('amount'))
                        phist = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__username=susername)
                except:
                    pass
                return render(request,"admin/rcard/paymentReport.html",{'form':paymentfilterform,'reseller':reseller,'phist':phist,'sum':bsum['amount__sum'],'user':userdetails,'filter':filter})
            else:
                return redirect(rcardpaymentReport)
        else:
            return redirect(rcardpaymentReport)
    else:
        return redirect(LoginPage)

def addRCardBrand(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"admin/rcard/addrcardbrand.html",{'form':AddRCardBrands,'user':userdetails})
    else:
        return redirect(LoginPage)

def submitRCardBrands(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = AddRCardBrands(request.POST, request.FILES)
            #print(form.errors)
            if form.is_valid():
                branddata=form.save()
                messages.success(request, 'Successfully Added The Brands')
                return redirect(addRCardBrand)
            else:
                messages.warning(request, form.errors)
                return redirect(addRCardBrand)
        else:
            return redirect(addRCardBrand)
    else:
        return redirect(LoginPage)

def manageRCardBrands(request):
    if request.session.has_key("user"):
        brands = rcardBrands.objects.all()
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"admin/rcard/managercardbrand.html",{'brands':brands,'user':userdetails})
    else:
        return redirect(LoginPage)

def assignRCardBrands(request):
    if request.session.has_key("user"):
        brands = rcardBrands.objects.all()
        #brands = rcardProducts.objects.filter(status=True).order_by('brand').values('brand').annotate(count=Count('brand')).values('brand__id','brand__brand','brand__denomination','count','brand__description','brand__logo','brand__currency')
        print(brands)
        resellers = UserData.objects.filter(postId="Reseller")
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"admin/rcard/assignRcardbrand.html",{'brands':brands,'resellers':resellers,'user':userdetails})
    else:
        return redirect(LoginPage)

def addrcardProduct(request):
    if request.session.has_key("user"):
        choices=rcardBrands.objects.all().values('id', 'brand')
        userdetails = UserData.objects.get(username=request.session["user"])
        #print(choices)
        return render(request,"admin/rcard/addrcardproduct.html",{'productform':AddRcardProducts,'brandform':AddRCardBrands,'choices':choices,'user':userdetails})
    else:
        return redirect(LoginPage)

def submitrcardProducts(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            try:
                form = AddRcardProducts(request.POST or None)
                if form.is_valid():
                    brandid = form.cleaned_data.get("brand")
                    username = form.cleaned_data.get("username")
                    password = form.cleaned_data.get("password")
                    res=rcardProducts.objects.filter(username = username).exists()
                    print(res)
                    res1=rcardupproducts.objects.filter(username = username).exists()
                    print(res1)
                    if(res or res1):
                        messages.warning(request, 'Product is alreday updated in Csv log. Go and spent the product')
                    else:
                        product = rcardProducts()
                        branddet = rcardBrands.objects.get(id=brandid)
                        product.brand = branddet
                        product.username = username
                        product.denomination = branddet.denomination
                        product.save()
                        messages.success(request, 'Successfully Added The Products')
                    return redirect(addrcardProduct)
                else:
                    messages.warning(request, form.errors)
                    return redirect(addrcardProduct)
            except:
                return redirect(addrcardProduct)
        else:
            return redirect(addrcardProduct)
    else:
        return redirect(LoginPage)


def rcardmanageProduct(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        product = rcardProducts.objects.all().order_by('-cdate')[:5000]
        return render(request,"admin/rcard/manageProduct.html",{'products':product,'user':userdetails})
    else:
        return redirect(LoginPage)

def saveassignRCardBrands(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            try:
                reseller = request.POST.get('username', None)
                values = request.POST.get('values', None)
                states = request.POST.get('states', None)
                brands = request.POST.get('brands', None)
                margins = request.POST.get('margins', None)
                v = values.split(',')
                s = states.split(',')
                b = brands.split(',')
                m = margins.split(',')
                username = request.session["user"]
                assignedby = UserData.objects.get(username=username)
                assignedto = UserData.objects.get(username=reseller)
                for i in range(0,len(s)):
                    if(int(s[i])==0):
                        print(True)
                        brandid=b[int(i)]
                        brdet=rcardBrands.objects.get(id=brandid)
                        print(brdet)
                        try:
                            vdt = rcardAssignments.objects.get(brand=brdet,assignedby=assignedby,assignedto=assignedto)
                            vdt.delete()
                            vadt = rcardAssignments.objects.filter(brand=brdet,assignedby=assignedto)
                            for i in vadt:
                                try:
                                    ud = rcardAssignments.objects.filter(brand=brdet,assignedby=i.assignedto)
                                    ud.delete()
                                except rcardAssignments.DoesNotExist:
                                    pass;
                            print(vadt)
                            vadt.delete()
                        except:
                            print("Error")
                    else:
                        print(False)
                        brandid=b[int(i)]
                        brdet=rcardBrands.objects.get(id=brandid)
                        try:
                            assdet = rcardAssignments.objects.get(brand=brdet,assignedby=assignedby,assignedto=assignedto)
                            assdet.margin = Decimal(v[int(i)])
                            assdet.save()
                        except rcardAssignments.DoesNotExist:
                            vass = rcardAssignments()
                            vass.brand=brdet
                            vass.assignedto=assignedto
                            vass.assignedby=assignedby
                            vass.margin = Decimal(v[int(i)])
                            vass.save()
                data={"status":"Success"}
                return JsonResponse(data)
            except:
                return redirect({"status":"Error"})
        else:
            pass
    else:
        return redirect(LoginPage)

def rcardstore(request):
    if request.session.has_key("user"):
        try:
            ads = adverisements.objects.filter(adtype="Image",ctype="Rcard").order_by('-id')[:10]
            rcardproducts = rcardProducts.objects.filter(status=True).order_by('brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
            some_list = []
            data = dict()
            for i in rcardproducts:
                brandname=i["brand__brand"]
                bd=brandname.split(' ')
                bname=bd[0]
                print(bname)
                if any(bname in s for s in some_list):
                    pass
                else:
                    some_list.append(bname)

            totalfil=len(some_list)
            if(totalfil != 0):
                classlist=[]
                for j in range(0,totalfil):
                    if(j==0):
                        classlist.append("btn-warning")
                    else:
                        classlist.append("btn-success")
                    btnlist = zip(some_list, classlist)
                    print(btnlist)
                    item=rcardProducts.objects.filter(status=True,brand__brand__contains=some_list[0]).order_by('brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
                    userdetails = UserData.objects.get(username=request.session["user"])
            else:
                item=None
                btnlist=None
                userdetails = UserData.objects.get(username=request.session["user"])
            return render(request,"admin/rcard/rcardstore.html",{'rcardproducts':item,'btnlist':btnlist,'user':userdetails,'ads':ads})
        except:
            pass
    else:
        return redirect(LoginPage)


def filteredrcardstore(request,brand):
    if request.session.has_key("user"):
        try:
            ads = adverisements.objects.filter(adtype="Image",ctype="Rcard").order_by('-id')[:10]
            rcardproducts = rcardProducts.objects.filter(status=True).order_by('brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
            some_list = []
            data = dict()
            for i in rcardproducts:
                brandname=i["brand__brand"]
                bd=brandname.split(' ')
                bname=bd[0]
                #print(bname)
                if any(bname in s for s in some_list):
                    pass
                else:
                    some_list.append(bname)
            totalfil=len(some_list)
            position=0
            for index, inbrand in enumerate(some_list):
                if inbrand == brand:
                    position=index
            classlist=[]
            for j in range(0,totalfil):
                if(j==position):
                    classlist.append("btn-warning")
                else:
                    classlist.append("btn-success")
            print(classlist)
            btnlist = zip(some_list, classlist)
            #print(btnlist)
            item=rcardProducts.objects.filter(status=True,brand__brand__contains=brand).order_by('brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
            userdetails = UserData.objects.get(username=request.session["user"])
            return render(request,"admin/rcard/rcardstore.html",{'rcardproducts':item,'btnlist':btnlist,'totalfil':totalfil,'user':userdetails,'ads':ads})
        except:
            pass;
    else:
        return redirect(LoginPage)

def rcardreport(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        username=request.session["user"]
        last_month = datetime.today() - timedelta(days=1)
        vcloudtxns = vcloudtransactions.objects.filter(date__gte=last_month,sponser1__username=username).order_by('-date')
        #vcloudtxns = vcloudtransactions.objects.all().order_by('-date')
        reseller=UserData.objects.filter(sponserId=username,postId="Reseller")
        resellerlist=list()
        vcbrand=vcloudBrands.objects.all()
        vcbrandlist=list()
        for b in vcbrand:
            branddata={'brand':b.brand}
            vcbrandlist.append(branddata)

        for i in reseller:
            resellerdata={'username':i.username,'name':i.name}
            resellerlist.append(resellerdata)
        content=list()
        noofrecords=0
        productsum =0
        quantitysum =0
        profitsum =0
        for i in vcloudtxns:
            data={"id":i.id,"saleduser":i.sponser2.name,"role":i.sponser2.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(i.denominations*i.quantity),"profit":i.margin1,"rtype":i.rtype}
            content.append(data)
            productsum=productsum+(i.denominations*i.quantity)
            quantitysum=quantitysum+i.quantity
            profitsum = profitsum+i.margin1
        box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum}
        return render(request,"admin/rcard/rcardreport.html",{'filterform':vcloudreportfilterform,'products':content,'user':userdetails,'reseller':resellerlist, 'brand':vcbrandlist,'box':box_data,'date':last_month})
    else:
        return redirect(LoginPage)

def filterrcard_report(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            try:
                form = vcloudreportfilterform(request.POST or None)
                print(form.errors)
                if form.is_valid():
                    username=request.session["user"]
                    fromdate=form.cleaned_data.get("fromdate")
                    todate=form.cleaned_data.get("todate")
                    usertype=form.cleaned_data.get("usertype")
                    print(usertype)
                    fusername=form.cleaned_data.get("username")
                    type=form.cleaned_data.get("type")
                    brand=form.cleaned_data.get("brand")
                    userdetails = UserData.objects.get(username=request.session["user"])
                    fuser=''
                    if(fusername!='All'):
                        filterdata=UserData.objects.get(username=fusername)
                        fuser=filterdata.name
                    else:
                        fuser=fusername
                    filter={'ffdate':fromdate,'ttdate':todate,'fuser':fuser}
                    reseller=UserData.objects.filter(sponserId=username,postId="Reseller")
                    resellerlist=list()
                    vcbrand=vcloudBrands.objects.all()
                    vcbrandlist=list()
                    for b in vcbrand:
                        branddata={'brand':b.brand}
                        vcbrandlist.append(branddata)

                    for i in reseller:
                        resellerdata={'username':i.username,'name':i.name}
                        resellerlist.append(resellerdata)

                    content=list()
                    noofrecords = 0
                    productsum = 0
                    quantitysum = 0
                    profitsum = 0
                    vcloudtxns=vcloudtransactions()
                    try:
                        print(usertype)
                        print(fusername)
                        print(type)
                        print(brand)
                        if(usertype=="All" and fusername=="All" and type=="All" and brand=="All"):
                            vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser1__username=username).order_by('-date')
                            print("One")
                        elif(usertype=="All" and fusername=="All" and type=="All" and brand !="All"):
                            print("TWo")
                            vcloudtxns==vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser1__username=username, brand=brand).order_by('-date')
                        elif(usertype=="All" and fusername=="All" and type !="All" and brand =="All"):
                            print("Three")
                            vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser1__username=username, type=type).order_by('-date')
                        elif(usertype=="All" and fusername=="All" and type !="All" and brand !="All"):
                            print("four")
                            vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser1__username=username, brand=brand).order_by('-date')
                        elif(usertype=="All" and fusername!="All" and type !="All" and brand !="All"):
                            print('five')
                            vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, type=type, sponser1__username=username, sponser2__username=fusername, brand=brand).order_by('-date')
                        elif(usertype !="All" and fusername =="All" and type =="All" and brand !="All"):
                            print('Six')
                            vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser2__type=usertype, sponser1__username=username).order_by('-date')
                        elif(usertype !="All" and fusername =="All" and type =="All" and brand =="All"):
                            print('Six')
                            vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser1__username=username, sponser2__postId=usertype).order_by('-date')
                        elif(usertype =="All" and fusername !="All" and type =="All" and brand =="All"):
                            print('Six')
                            vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser1__username=username, sponser2__username=fusername).order_by('-date')
                        elif(usertype !="All" and fusername !="All" and type =="All" and brand =="All"):
                            print('Six')
                            vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser1__username=username, sponser2__username=fusername).order_by('-date')
                        else:
                            vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser1__username=username, sponser2__username=fusername,brand=brand).order_by('-date')
                        print(vcloudtxns)
                        for i in vcloudtxns:
                            data={"id":i.id,"saleduser":i.sponser2.name,"role":i.sponser2.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(i.denominations*i.quantity),"profit":i.margin1,"rtype":i.rtype}
                            content.append(data)
                            productsum=productsum+(i.denominations*i.quantity)
                            quantitysum=quantitysum+i.quantity
                            profitsum = profitsum+i.margin1
                    except:
                        pass
                    box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum}
                    return render(request,"admin/rcard/rcardreport.html",{'filterform':vcloudreportfilterform,'products':content,'user':userdetails,'reseller':resellerlist, 'brand':vcbrandlist,'box':box_data,'filter':filter})
                else:
                    return redirect(rcardreport)
            except:
                return redirect(rcardreport)
        else:
            return redirect(rcardreport)
    else:
        return redirect(LoginPage)

#________________________________________________________________Reseller_______________________________________________________________

#________________VCLOUD_______________

def resellervcloudhomePage(request):
    if request.session.has_key("user"):
        try:
            username = request.session["user"]
            #print(last_month)
            reseller = UserData.objects.filter(sponserId=username,postId="Sub_Reseller")
            #print(reseller)
            resellerlist=list()
            for i in reseller:
                resellerdata={'username':i.username,'name':i.name}
                resellerlist.append(resellerdata)
            username = request.session["user"]
            type = request.session["usertype"]
            try:
                user = UserData.objects.get(username = username, postId = type)
            except UserData.DoesNotExist:
                return redirect(LoginPage)
            userdetails = UserData.objects.get(username=request.session["user"])
            username=request.session["user"]
            last_month = datetime.today() - timedelta(days=1)
            vcloudtxns = vcloudtransactions.objects.filter(date__gte=last_month,sponser2__username=username,type="Vcloud").order_by('-date')
            content=list()
            topuser=list()
            noofrecords=0
            productsum =0
            quantitysum =0
            profitsum =0
            count=0
            for i in vcloudtxns:
                count=count+1
                cost=i.denominations+i.margin1
                productsum=productsum+(cost*i.quantity)
                quantitysum=quantitysum+i.quantity
                if(i.saleduser.username==username):
                    profit=0
                    #data3={'user':i.sponser2.name,'amount':(i.denominations*i.quantity)}
                    data={"id":i.id,"saleduser":i.sponser2.name,"role":i.sponser2.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                    content.append(data)
                    profitsum = profitsum+profit
                else:
                    profit=i.margin2*i.quantity
                    data3={'user':i.sponser3.name,'amount':(cost*i.quantity)}
                    topuser.append(data3)
                    data={"id":i.id,"saleduser":i.sponser3.name,"role":i.sponser3.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                    content.append(data)
                    profitsum = profitsum+profit
            box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum,'noofrecords':count}
            brand = vcloudAssignments.objects.filter(assignedto=username).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description','margin')
            product=list()
            print(brand)
            for i in brand:
                print(i['brand__id'])
                pd=vcloudProducts.objects.filter(brand=i['brand__id'],status=True).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
                lpd=list(pd)
                count=0
                if not lpd:
                    pass
                    #print("Haiii")
                else:
                    username=request.session["user"]
                    productcost=Decimal(lpd[0]['brand__denomination'])
                    print(productcost)
                    while(True):
                        userdet2=UserData.objects.get(username=username)
                        print(userdet2)
                        margindet=vcloudAssignments.objects.filter(assignedto=username,brand__brand=i['brand__brand']).values('margin')
                        if(userdet2.postId=="Admin"):
                            break;
                        else:
                            #print(margindet[0]['margin'])
                            productcost = Decimal(productcost)+Decimal(margindet[0]['margin'])
                            #print(productcost)
                        username=userdet2.sponserId
                        count=int(count)+1
                    data={"brand":lpd[0]['brand__brand'],'rate':productcost}
                    product.append(data)
                    #print(content)
            print(product)
            list3=list()
            sorted_users = sorted(topuser, key=itemgetter('user'))

            for key, group in itertools.groupby(sorted_users, key=lambda x:x['user']):
                amountsum=0
                for g in group:
                    amountsum=amountsum+g["amount"]
                    #print(amountsum)
                data5={'user':key,'amount':amountsum}
                list3.append(data5)
            return render(request,"reseller/vcloud/dashboard-vcloud.html",{'filterform':vcloudDashboardfilter,'reseller':resellerlist,'recenttransactions':content,'products':product,'user':user,'topuser':list3,'last_month':last_month,'boxval':box_data})
        except Exception as e:
            print(e);
            pass;
            #return render(request,"reseller/vcloud/dashboard-vcloud.html",{'filterform':vcloudDashboardfilter,'reseller':resellerlist,'recenttransactions':content,'products':product,'user':user,'topuser':list3,'last_month':last_month,'boxval':box_data})
    else:
        return redirect(LoginPage)

def filterresellervcloudhomepage(request):
    if request.session.has_key('user'):
        if request.method == "POST":
            try:
                form = vcloudDashboardfilter(request.POST or None)
                print(form.errors)
                if form.is_valid():
                    currentuser=request.session["user"]
                    fromdate=form.cleaned_data.get("fromdate")
                    todate=form.cleaned_data.get("todate")
                    usertype=form.cleaned_data.get("usertype")
                    uuusername=form.cleaned_data.get("username")
                    #mffromdate=datetime.strptime(fromdate, '%b %d %Y %I:%M%p')
                    print(type(fromdate))
                    print(fromdate.strftime("%B %d, %Y"))
                    last_month=fromdate.strftime("%B %d, %I:%M %p")+" To "+todate.strftime("%B %d, %I:%M %p")
                    reseller = UserData.objects.filter(sponserId=currentuser,postId="Sub_Reseller")
                    #print(reseller)
                    resellerlist=list()
                    for i in reseller:
                        resellerdata={'username':i.username,'name':i.name}
                        resellerlist.append(resellerdata)
                    #print(username)
                    userdetails = UserData.objects.get(username=request.session["user"])
                    vcloudtxns = vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate,sponser2__username=currentuser,type="Vcloud",sponser3__username=uuusername).order_by('-date')
                    content=list()
                    topuser=list()
                    noofrecords=0
                    productsum =0
                    quantitysum =0
                    profitsum =0
                    count=0
                    for i in vcloudtxns:
                        count=count+1
                        cost=i.denominations+i.margin1
                        productsum=productsum+(cost*i.quantity)
                        quantitysum=quantitysum+i.quantity
                        if(i.saleduser.username==username):
                            profit=0
                            #data3={'user':i.sponser2.name,'amount':(i.denominations*i.quantity)}
                            data={"id":i.id,"saleduser":i.sponser2.name,"role":i.sponser2.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                            content.append(data)
                            profitsum = profitsum+profit
                        else:
                            profit=i.margin2*i.quantity
                            data3={'user':i.sponser3.name,'amount':(cost*i.quantity)}
                            topuser.append(data3)
                            data={"id":i.id,"saleduser":i.sponser3.name,"role":i.sponser3.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                            content.append(data)
                            profitsum = profitsum+profit
                    box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum,'noofrecords':count}
                    brand = vcloudAssignments.objects.filter(assignedto=currentuser).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description','margin')
                    product=list()
                    print(brand)
                    for i in brand:
                        print(i['brand__id'])
                        pd=vcloudProducts.objects.filter(brand=i['brand__id'],status=True).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
                        lpd=list(pd)
                        count=0
                        if not lpd:
                            pass
                        else:
                            username=request.session["user"]
                            productcost=Decimal(lpd[0]['brand__denomination'])
                            print(productcost)
                            while(True):
                                userdet2=UserData.objects.filter(username=username).values('sponserId','postId')
                                print(userdet2)
                                margindet=vcloudAssignments.objects.filter(assignedto=username,brand__brand=i['brand__brand']).values('margin')
                                if(userdet2[0]['postId']=="Admin"):
                                    break;
                                else:
                                    print(margindet[0]['margin'])
                                    productcost = Decimal(productcost)+Decimal(margindet[0]['margin'])
                                    print(productcost)
                                    username=userdet2[0]['sponserId']
                                count=int(count)+1
                            data={"brand":lpd[0]['brand__brand'],'rate':productcost}
                            product.append(data)
                            #print(content)
                    print(product)
                    list3=list()
                    sorted_users = sorted(topuser, key=itemgetter('user'))

                    for key, group in itertools.groupby(sorted_users, key=lambda x:x['user']):
                        amountsum=0
                        for g in group:
                            amountsum=amountsum+g["amount"]
                            #print(amountsum)
                        data5={'user':key,'amount':amountsum}
                        list3.append(data5)
                    return render(request,"reseller/vcloud/dashboard-vcloud.html",{'filterform':vcloudDashboardfilter,'reseller':resellerlist,'recenttransactions':content,'products':product,'user':userdetails,'topuser':list3,'last_month':last_month,'boxval':box_data})
                else:
                    print("Haiii0")
                    return redirect(resellervcloudhomePage)
            except:
                print("Haiii1")
                return redirect(resellervcloudhomePage)
        else:
            print("Haiii2")
            return(resellervcloudhomePage)
    else:
        return redirect(LoginPage)


def resellervcloudaddReseller(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"reseller/vcloud/addReseller.html",{'form':AddUserDataForm,'user':userdetails})
    else:
        return redirect(LoginPage)

def resellervcloudnewReseller(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = AddUserDataForm(request.POST or None)
            print(form.errors)
            if form.is_valid():
                username=form.cleaned_data.get("username")
                password=form.cleaned_data.get("password")
                hashkey = username+password
                hash = hashlib.sha256(hashkey.encode()).hexdigest()
                sponser = request.session["user"]
                sponseruser=UserData.objects.get(username=sponser)
                Userdata=form.save(commit=False)
                Userdata.postId="Sub_Reseller"
                Userdata.sponserId = sponseruser
                Userdata.status = True
                Userdata.balance = 0
                Userdata.targetAmt = 0
                Userdata.rentalAmt = 0
                Userdata.dcard_status = True
                Userdata.rcard_status = True
                Userdata.password = hash
                Userdata.save()
                messages.success(request, 'Successfully Added')
                return redirect(resellervcloudaddReseller)
            else:
                userdetails = UserData.objects.get(username=request.session["user"])
                messages.warning(request, form.errors)
                form = AddUserDataForm()
                return render(request,"reseller/vcloud/addReseller.html",{'form':AddUserDataForm,'user':userdetails})
        else:
            userdetails = UserData.objects.get(username=request.session["user"])
            form = AddUserDataForm()
            return render(request,"reseller/vcloud/addReseller.html",{'form':AddUserDataForm,'user':userdetails})
    else:
        return redirect(LoginPage)

def resellervcloudviewReseller(request):
    if request.session.has_key("user"):
        username = request.session["user"]
        userdet = UserData.objects.get(username=username)
        print(userdet)
        try:
            resellers = UserData.objects.filter(postId="Sub_Reseller",sponserId=username)
        except UserData.DoesNotExist:
            resellers = None
        return render(request,"reseller/vcloud/viewResellers.html",{'resellers':resellers,'user':userdet})
    else:
        return redirect(LoginPage)

def resellervcloudaddUser(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"reseller/vcloud/addUser.html",{'form':AddUserDataForm,'user':userdetails})
    else:
        return redirect(LoginPage)

def resellervcloudnewUser(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = AddUserDataForm(request.POST or None)
            print(form.errors)
            if form.is_valid():
                username=form.cleaned_data.get("username")
                password=form.cleaned_data.get("password")
                hashkey = username+password
                hash = hashlib.sha256(hashkey.encode()).hexdigest()
                print(username)
                print(password)
                print(hash)
                sponser = request.session["user"]
                sponseruser=UserData.objects.get(username=sponser)
                Userdata=form.save(commit=False)
                Userdata.postId="User"
                Userdata.sponserId = sponseruser
                Userdata.status = True
                Userdata.balance = 0
                Userdata.targetAmt = 0
                Userdata.rentalAmt = 0
                Userdata.dcard_status = True
                Userdata.rcard_status = True
                Userdata.password = hash
                Userdata.save()
                messages.success(request, 'Successfully Added')
                return redirect(resellervcloudaddUser)
            else:
                userdetails = UserData.objects.get(username=request.session["user"])
                messages.warning(request, form.errors)
                form = AddUserDataForm()
                return render(request,"reseller/vcloud/addUser.html",{'form':AddUserDataForm,'user':userdetails})
        else:
            userdetails = UserData.objects.get(username=request.session["user"])
            form = AddUserDataForm()
            return render(request,"reseller/vcloud/addUser.html",{'form':AddUserDataForm,'user':userdetails})
    else:
        return redirect(LoginPage)

def resellervcloudviewUser(request):
    if request.session.has_key("user"):
        username = request.session["user"]
        resellers = UserData.objects.filter(postId="User",sponserId=username)
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"reseller/vcloud/viewUser.html",{'resellers':resellers,'user':userdetails})
    else:
        return redirect(LoginPage)

def resellervcloudprofile(request):
    if request.session.has_key("user"):
        user = request.session["user"]
        userDet = UserData.objects.get(username=user)
        return render(request,"reseller/vcloud/editProfile.html",{'user':userDet})
    else:
        return redirect(LoginPage)

def resellervcloudeditProfile(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            user = request.session["user"]
            name = request.POST.get('name', None)
            address = request.POST.get('address', None)
            email = request.POST.get('email', None)
            mobileno = request.POST.get('mobileno', None)
            userDet = UserData.objects.get(username=user)
            userDet.name = name
            userDet.address = address
            userDet.email = email
            userDet.mobileno = mobileno
            userDet.save()
            messages.success(request, 'Successfully Updated')
            return redirect(resellervcloudprofile)
        else:
            messages.warning(request,'Internal Error Occured')
            return redirect(resellervcloudprofile)
    else:
        return redirect(LoginPage)

def resellervcloudbalanceTransfer(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        bthist=balanceTransactionReport.objects.filter(source=userdetails,category="BT").order_by('-date')
        #print(bthist)
        return render(request,"reseller/vcloud/balanceTransfer.html",{'bthist':bthist,'user':userdetails})
    else:
        return redirect(LoginPage)

def resellervcloudSubmitBalanceTransfer(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            userType = request.POST.get('userType', None)
            user = request.POST.get('users', None)
            amount = request.POST.get('amount', None)
            userdet = UserData.objects.get(username=user)
            bal = userdet.balance
            newbal=bal+Decimal(amount)
            cdbal = userdet.targetAmt
            newcdbal = cdbal-Decimal(amount)
            userdet.targetAmt = newcdbal
            userdet.balance = newbal
            userdet.save()
            userdetails = UserData.objects.get(username=request.session["user"])
            btreport = balanceTransactionReport()
            btreport.source = userdetails
            btreport.destination = userdet
            btreport.category = "BT"
            btreport.amount = amount
            btreport.pbalance = bal
            btreport.nbalance = newbal
            btreport.cramount = newcdbal
            btreport.remarks = 'Added To Balance'
            btreport.save()
            messages.success(request, 'Successfully Updated The balance')
            return redirect(resellervcloudbalanceTransfer)
            #userdata=UserData.objects.get(username=)
        else:
            messages.warning(request, 'Internal Error Occured')
            return redirect(resellervcloudbalanceTransfer)
    else:
        return redirect(LoginPage)


def resellervcloudaddPayment(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        phist=fundTransactionReport.objects.filter(source=userdetails).order_by('-date')
        return render(request,"reseller/vcloud/addPayment.html",{'phist':phist,'user':userdetails})
    else:
        return redirect(LoginPage)

def resellervcloudsubmitPayment(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            userType = request.POST.get('userType', None)
            user = request.POST.get('users', None)
            amount = request.POST.get('amount', None)
            remarks = request.POST.get('remarks', None)
            userdet = UserData.objects.get(username=user)
            obalance = userdet.targetAmt
            cdbal = userdet.targetAmt
            newcdbal = cdbal+Decimal(amount)
            userdet.targetAmt = newcdbal
            userdet.save()
            closeuser = UserData.objects.get(username=user)
            userdetails = UserData.objects.get(username=request.session["user"])
            ftreport=fundTransactionReport()
            ftreport.source = userdetails
            ftreport.destination = userdet
            ftreport.obalance = obalance
            ftreport.cbalance = closeuser.targetAmt
            ftreport.role = userType
            ftreport.amount = amount
            ftreport.balance = newcdbal
            ftreport.remarks = remarks
            ftreport.save()
            messages.success(request, 'Successfully Updated The balance')
            return redirect(resellervcloudaddPayment)
        else:
            messages.warning(request, 'Internal Error Occured')
            return redirect(resellervcloudaddPayment)
    else:
        return redirect(LoginPage)

def resellervcloudbalanceTransferReport(request):
    if request.session.has_key("user"):
        username = request.session["user"]
        userdetails = UserData.objects.get(username=request.session["user"])
        reseller = UserData.objects.filter(sponserId=username,postId="Sub_Reseller")
        fromsum = balanceTransactionReport.objects.filter(source=userdetails,category='BT').aggregate(Sum('amount'))
        tosum = balanceTransactionReport.objects.filter(destination=userdetails,category='BT').aggregate(Sum('amount'))
        bthist = balanceTransactionReport.objects.filter(source=userdetails) | balanceTransactionReport.objects.filter(destination=userdetails).order_by('-date')
        return render(request,"reseller/vcloud/balanceTransferReport.html",{'form':balancetransferfilterform,'reseller':reseller,'bthist':bthist,'fromsum':fromsum['amount__sum'],'tosum':tosum['amount__sum'],'user':userdetails})
    else:
        return redirect(LoginPage)

def filterresellervcloudbtreport(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            form = balancetransferfilterform(request.POST or None)
            print(form.errors)
            if form.is_valid():
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                usertype=form.cleaned_data.get("usertype")
                susername=form.cleaned_data.get("username")
                username = request.session["user"]
                #fuser=UserData.objects.get(username=susername)
                filter={'ffdate':fromdate,'ttdate':todate,'fuser':susername}
                userdetails = UserData.objects.get(username=request.session["user"])
                reseller = UserData.objects.filter(sponserId=username,postId="Sub_Reseller")
                fromsum=None
                tosum=None
                bthist=None
                try:
                    if(usertype == "Self"):
                        fromsum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails).aggregate(Sum('amount'))
                        tosum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdetails).aggregate(Sum('amount'))
                        bthist = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdetails)
                    elif(usertype == "All" and susername == "All"):
                        fromsum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails).aggregate(Sum('amount'))
                        tosum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdetails).aggregate(Sum('amount'))
                        bthist = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails)
                    elif(usertype!="All" and susername == "All"):
                        fromsum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__postId=usertype).aggregate(Sum('amount'))
                        tosum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdetails).aggregate(Sum('amount'))
                        bthist = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__postId=usertype)
                    else:
                        fromsum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__username=susername).aggregate(Sum('amount'))
                        tosum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdetails).aggregate(Sum('amount'))
                        bthist = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__username=susername)
                except:
                    pass
                return render(request,"reseller/vcloud/balanceTransferReport.html",{'form':balancetransferfilterform,'reseller':reseller,'bthist':bthist,'fromsum':fromsum['amount__sum'],'tosum':tosum['amount__sum'],'user':userdetails,'filter':filter})
            else:
                return redirect(resellervcloudbalanceTransferReport)
        else:
            return redirect(resellervcloudbalanceTransferReport)
    else:
        return redirect(LoginPage)

def resellervcloudpaymentReport(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        reseller = UserData.objects.filter(sponserId=request.session["user"],postId="Sub_Reseller")
        phist = fundTransactionReport.objects.filter(source=userdetails).order_by('-date') | fundTransactionReport.objects.filter(destination=userdetails).order_by('-date')
        bsum = fundTransactionReport.objects.filter(source=userdetails).aggregate(Sum('amount'))
        return render(request,"reseller/vcloud/paymentReport.html",{'form':paymentfilterform,'reseller':reseller,'phist':phist,'sum':bsum['amount__sum'],'user':userdetails})
    else:
        return redirect(LoginPage)

def filterresellervcloudpaymentreport(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            form = balancetransferfilterform(request.POST or None)
            print(form.errors)
            if form.is_valid():
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                usertype=form.cleaned_data.get("usertype")
                susername=form.cleaned_data.get("username")
                username = request.session["user"]
                filter={'ffdate':fromdate,'ttdate':todate,'fuser':susername}
                userdetails = UserData.objects.get(username=request.session["user"])
                reseller = UserData.objects.filter(sponserId=username,postId="Sub_Reseller")
                print(usertype)
                bsum=None
                phist=None
                try:
                    if(usertype == "Self" ):
                        bsum = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdetails).aggregate(Sum('amount'))
                        phist = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdetails)
                    elif(usertype == "All" and susername == "All"):
                        bsum = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails).aggregate(Sum('amount'))
                        phist = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails)
                        print(phist)
                        print("phist")
                    elif(usertype!="All" and susername == "All"):
                        print(usertype)
                        bsum = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails).aggregate(Sum('amount'))
                        phist = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails, destination__postId=usertype)
                        print("Haiii")
                    else:
                        bsum = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__username=susername).aggregate(Sum('amount'))
                        phist = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__username=susername)
                except Exception as e:
                    print(e)
                    pass
                return render(request,"reseller/vcloud/paymentReport.html",{'form':paymentfilterform,'reseller':reseller,'phist':phist,'sum':bsum['amount__sum'],'user':userdetails,'filter':filter})
            else:
                return redirect(resellervcloudpaymentReport)
        else:
            return redirect(resellervcloudpaymentReport)
    else:
        return redirect(LoginPage)

def resellervcloudreport(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        username=request.session["user"]
        last_month = datetime.today() - timedelta(days=1)
        vcloudtxns = vcloudtransactions.objects.filter(date__gte=last_month,sponser2__username=username).order_by('-date')
        #vcloudtxns = vcloudtransactions.objects.all().order_by('-date')
        reseller=UserData.objects.filter(sponserId=username,postId="Reseller")
        resellerlist=list()
        vcbrand=vcloudBrands.objects.all()
        vcbrandlist=list()
        for b in vcbrand:
            branddata={'brand':b.brand}
            vcbrandlist.append(branddata)

        for i in reseller:
            resellerdata={'username':i.username,'name':i.name}
            resellerlist.append(resellerdata)
        content=list()
        noofrecords=0
        productsum =0
        quantitysum =0
        profitsum =0
        cost=0
        for i in vcloudtxns:
            cost=i.denominations+i.margin1
            productsum=productsum+(cost*i.quantity)
            quantitysum=quantitysum+i.quantity
            if(i.saleduser.username==username):
                profit=0
                data={"id":i.id,"saleduser":i.sponser2.name,"role":i.sponser2.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                content.append(data)
                profitsum = profitsum+profit
            else:
                profit=(i.margin2*i.quantity)
                data={"id":i.id,"saleduser":i.sponser3.name,"role":i.sponser3.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                content.append(data)
                profitsum = profitsum+profit

        box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum}
        return render(request,"reseller/vcloud/vcloudreport.html",{'filterform':vcloudreportfilterform,'products':content,'user':userdetails,'reseller':resellerlist, 'brand':vcbrandlist,'box':box_data,'date':last_month})
    else:
        return redirect(LoginPage)

def filterresellervcloud_report(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            form = vcloudreportfilterform(request.POST or None)
            print(form.errors)
            if form.is_valid():
                username=request.session["user"]
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                usertype=form.cleaned_data.get("usertype")
                fusername=form.cleaned_data.get("username")
                type=form.cleaned_data.get("type")
                brand=form.cleaned_data.get("brand")
                fuser=''
                if(fusername!='All'):
                    filterdata=UserData.objects.get(username=fusername)
                    fuser=filterdata.name
                else:
                    fuser=fusername
                filter={'ffdate':fromdate,'ttdate':todate,'fuser':fuser}
                reseller=UserData.objects.filter(sponserId=username,postId="Sub_Reseller")
                resellerlist=list()
                vcbrand=vcloudBrands.objects.all()
                vcbrandlist=list()
                for b in vcbrand:
                    branddata={'brand':b.brand}
                    vcbrandlist.append(branddata)

                for i in reseller:
                    resellerdata={'username':i.username,'name':i.name}
                    resellerlist.append(resellerdata)

                username=request.session["user"]
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                usertype=form.cleaned_data.get("usertype")
                print(usertype)
                fusername=form.cleaned_data.get("username")
                type=form.cleaned_data.get("type")
                brand=form.cleaned_data.get("brand")
                userdetails = UserData.objects.get(username=request.session["user"])
                fuser=''
                if(fusername!='All'):
                    filterdata=UserData.objects.get(username=fusername)
                    fuser=filterdata.name
                else:
                    fuser=fusername
                filter={'ffdate':fromdate,'ttdate':todate,'fuser':fuser}
                reseller=UserData.objects.filter(sponserId=username,postId="Reseller")
                resellerlist=list()
                vcbrand=vcloudBrands.objects.all()
                vcbrandlist=list()
                for b in vcbrand:
                    branddata={'brand':b.brand}
                    vcbrandlist.append(branddata)

                for i in reseller:
                    resellerdata={'username':i.username,'name':i.name}
                    resellerlist.append(resellerdata)

                content=list()
                noofrecords = 0
                productsum = 0
                quantitysum = 0
                profitsum = 0
                vcloudtxns=vcloudtransactions()
                try:
                    print(usertype)
                    print(fusername)
                    print(type)
                    print(brand)
                    if(usertype=="All" and fusername=="All" and type=="All" and brand=="All"):
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser2__username=username).order_by('-date')
                        print("One")
                    elif(usertype=="All" and fusername=="All" and type=="All" and brand !="All"):
                        print("TWo")
                        vcloudtxns==vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser2__username=username, brand=brand).order_by('-date')
                    elif(usertype=="All" and fusername=="All" and type !="All" and brand =="All"):
                        print("Three")
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser2__username=username, type=type).order_by('-date')
                    elif(usertype=="All" and fusername=="All" and type !="All" and brand !="All"):
                        print("four")
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser2__username=username, brand=brand).order_by('-date')
                    elif(usertype=="All" and fusername!="All" and type !="All" and brand !="All"):
                        print('five')
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, type=type, sponser2__username=username, sponser3__username=fusername, brand=brand).order_by('-date')
                    elif(usertype !="All" and fusername =="All" and type =="All" and brand !="All"):
                        print('Six')
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser3__postId=usertype, sponser2__username=username).order_by('-date')
                    elif(usertype !="All" and fusername =="All" and type =="All" and brand =="All"):
                        print('Six')
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser2__username=username, sponser3__postId=usertype).order_by('-date')
                    elif(usertype =="All" and fusername !="All" and type =="All" and brand =="All"):
                        print('Six')
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser2__username=username, sponser3__username=fusername).order_by('-date')
                    elif(usertype !="All" and fusername !="All" and type =="All" and brand =="All"):
                        print('Six')
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser2__username=username, sponser3__username=fusername).order_by('-date')
                    else:
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser2__username=username, sponser3__username=fusername,brand=brand).order_by('-date')
                    print(vcloudtxns)
                    for i in vcloudtxns:
                        cost=i.denominations+i.margin1
                        productsum=productsum+(cost*i.quantity)
                        quantitysum=quantitysum+i.quantity
                        if(i.saleduser.username==username):
                            profit=0
                            data={"id":i.id,"saleduser":i.sponser2.name,"role":i.sponser2.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                            content.append(data)
                            profitsum = profitsum+profit
                        else:
                            profit=(i.margin2*i.quantity)
                            data={"id":i.id,"saleduser":i.sponser3.name,"role":i.sponser3.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                            content.append(data)
                            profitsum = profitsum+profit
                except:
                    pass
                box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum}
                return render(request,"reseller/vcloud/vcloudreport.html",{'filterform':vcloudreportfilterform,'products':content,'user':userdetails,'reseller':resellerlist, 'brand':vcbrandlist,'box':box_data,'filter':filter})
            else:
                return redirect(resellervcloudreport)
        else:
            return redirect(resellervcloudreport)
    else:
        return redirect(LoginPage)


def resellervcloudStore(request):
    if request.session.has_key("user"):
        username=request.session["user"]
        ads = adverisements.objects.filter(adtype="Image",usertype="Reseller",ctype="Vcloud").order_by('-id')[:10]
        pdcts = vcloudAssignments.objects.filter(assignedto=username,brand__category="card with cutting").order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description','margin')
        #print(pdcts)
        data=dict()
        content = []
        for i in pdcts:
            #print(i['brand__id'])
            lpd=vcloudProducts.objects.filter(brand__id=i['brand__id'],status = True).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
            count=0
            if not lpd:
                pass
            else:
                username=request.session["user"]
                productcost=Decimal(lpd[0]['brand__denomination'])
                #print(productcost)
                while(True):
                    userdet2=UserData.objects.filter(username=username).values('sponserId','postId')
                    #print(userdet2)
                    margindet=vcloudAssignments.objects.filter(assignedto=username,brand__brand=i['brand__brand']).values('margin')
                    if(userdet2[0]['postId']=="Admin"):
                        break;
                    else:
                        #print(margindet[0]['margin'])
                        productcost = Decimal(productcost)+Decimal(margindet[0]['margin'])
                        #print(productcost)
                        username=userdet2[0]['sponserId']
                    count=int(count)+1
                data={"brand_id":lpd[0]['brand__id'],"brand__brand":lpd[0]['brand__brand'],'productcount':lpd[0]['productcount'],'brand__logo':lpd[0]['brand__logo'],'brand__denomination':productcost,'brand__currency':lpd[0]['brand__currency'],'brand__description':lpd[0]['brand__description']}
                content.append(data)
        buttonlist=["Cutting","Non Cutting"]
        buttonclass=["btn-warning","btn-success"]
        btnlist = zip(buttonlist, buttonclass)
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"reseller/vcloud/vcloudStore.html",{'pdcts':content,'btnlist':btnlist,'user':userdetails,'ads':ads})
    else:
        return redirect(LoginPage)

def resellerfilteredvcloudstore(request,brandtype):
    if request.session.has_key("user"):
        username=request.session["user"]
        buttonclass=[]
        ads = adverisements.objects.filter(adtype="Image",usertype="Reseller",ctype="Vcloud").order_by('-id')[:10]
        if(brandtype=="Cutting"):
            pdcts = vcloudAssignments.objects.filter(assignedto=username,brand__category="card with cutting").order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
            data=dict()
            content = []
            for i in pdcts:
                pd=vcloudProducts.objects.filter(brand=i['brand__id'],status=True).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
                lpd=list(pd)
                #print(lpd)
                #print(productcost)
                count=0
                if not lpd:
                    #break;
                    pass;
                else:
                    username=request.session["user"]
                    productcost=Decimal(lpd[0]['brand__denomination'])
                    print(productcost)
                    while(True):
                        userdet2=UserData.objects.filter(username=username).values('sponserId','postId')
                        #print(userdet2)
                        margindet=vcloudAssignments.objects.filter(assignedto=username,brand__brand=i['brand__brand']).values('margin')
                        if(userdet2[0]['postId']=="Admin"):
                            break;
                        else:
                            #print(margindet[0]['margin'])
                            productcost = Decimal(productcost)+Decimal(margindet[0]['margin'])
                            #print(productcost)
                            username=userdet2[0]['sponserId']
                        count=int(count)+1
                    data={"brand_id":lpd[0]['brand__id'],"brand__brand":lpd[0]['brand__brand'],'productcount':lpd[0]['productcount'],'brand__logo':lpd[0]['brand__logo'],'brand__denomination':productcost,'brand__currency':lpd[0]['brand__currency'],'brand__description':lpd[0]['brand__description']}
                    content.append(data)
                    #print(content)
            buttonclass=["btn-warning","btn-success"]
        else:
            pdcts = vcloudAssignments.objects.filter(assignedto=username,brand__category="card without cutting").order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
            data=dict()
            content = []
            for i in pdcts:
                pd=vcloudProducts.objects.filter(brand=i['brand__id'],status=True).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
                lpd=list(pd)
                #print(lpd)
                #print(productcost)
                count=0
                if not lpd:
                    #break;
                    #print("Haiii")
                    pass
                else:
                    username=request.session["user"]
                    productcost=Decimal(lpd[0]['brand__denomination'])
                    #print(productcost)
                    while(True):
                        userdet2=UserData.objects.filter(username=username).values('sponserId','postId')
                        print(userdet2)
                        margindet=vcloudAssignments.objects.filter(assignedto=username,brand__brand=i['brand__brand']).values('margin')
                        if(userdet2[0]['postId']=="Admin"):
                            break;
                        else:
                            #print(margindet[0]['margin'])
                            productcost = Decimal(productcost)+Decimal(margindet[0]['margin'])
                            #print(productcost)
                            username=userdet2[0]['sponserId']
                        count=int(count)+1
                    data={"brand_id":lpd[0]['brand__id'],"brand__brand":lpd[0]['brand__brand'],'productcount':lpd[0]['productcount'],'brand__logo':lpd[0]['brand__logo'],'brand__denomination':productcost,'brand__currency':lpd[0]['brand__currency'],'brand__description':lpd[0]['brand__description']}
                    content.append(data)
                    #print(content)
            buttonclass=["btn-success","btn-warning"]
        buttonlist=["Cutting","Non Cutting"]
        btnlist = zip(buttonlist, buttonclass)
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"reseller/vcloud/vcloudStore.html",{'pdcts':content,'btnlist':btnlist,'user':userdetails,'ads':ads})
    else:
        return redirect(LoginPage)

def resellersaveassignVcloudBrands(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            try:
                reseller = request.POST.get('username', None)
                values = request.POST.get('values', None)
                states = request.POST.get('states', None)
                brands = request.POST.get('brands', None)
                margins = request.POST.get('margins', None)
                v = values.split(',')
                s = states.split(',')
                b = brands.split(',')
                m = margins.split(',')
                username = request.session["user"]
                assignedby = UserData.objects.get(username=username)
                assignedto = UserData.objects.get(username=reseller)
                for i in range(0,len(s)):
                    if(int(s[i])==0):
                        print(True)
                        brandid=b[int(i)]
                        brdet=vcloudBrands.objects.get(id=brandid)
                        print(brdet)
                        try:
                            vdt = vcloudAssignments.objects.get(brand=brdet,assignedby=assignedby,assignedto=assignedto)
                            vdt.delete()
                            vadt = vcloudAssignments.objects.filter(brand=brdet,assignedby=assignedto)
                            print(vadt)
                            for i in vadt:
                                try:
                                    ud = vcloudAssignments.objects.filter(brand=brdet,assignedby=i.assignedto)
                                    ud.delete()
                                except Exception as e:
                                    print("inner "+str(e))
                            vadt.delete()
                        except vcloudAssignments.DoesNotExist:
                            print("Error")
                    else:
                        print(False)
                        brandid=b[int(i)]
                        brdet=vcloudBrands.objects.get(id=brandid)
                        try:
                            assdet = vcloudAssignments.objects.get(brand=brdet,assignedby=assignedby,assignedto=assignedto)
                            assdet.margin = Decimal(v[int(i)])
                            assdet.save()
                        except vcloudAssignments.DoesNotExist:
                            vass = vcloudAssignments()
                            vass.brand=brdet
                            vass.assignedto=assignedto
                            vass.assignedby=assignedby
                            vass.margin = Decimal(v[int(i)])
                            vass.save()
                data={"status":"Success"}
                return JsonResponse(data)
            except:
                return JsonResponse({"status":"Error"})
        else:
            pass
    else:
        return redirect(LoginPage)

def getvcloudproductcost(brand,username):
    print(brand)
    prdcts=vcloudBrands.objects.get(brand=brand)
    prdctcost = Decimal(prdcts.denomination)
    print(prdcts)
    margins=0
    while(True):
        userdet = UserData.objects.filter(username=username).values('sponserId','postId')
        pdct = vcloudAssignments.objects.filter(assignedto=username, brand__brand=brand).values('margin')
        if(pdct):
            if(userdet[0]['postId']=="Admin"):
                break
            else:
                prdctcost = prdctcost+Decimal(pdct[0]['margin'])
            username=userdet[0]['sponserId']
        else:
            break;
    return prdctcost

def resellerassignVcloudBrands(request):
    if request.session.has_key("user"):
        print("Haiii")
        brands = vcloudAssignments.objects.filter(assignedto=request.session["user"]).values('brand','brand__brand')
        print(brands)
        username=request.session["user"]
        costlist=list()
        brandlist=list()
        for j in brands:
            prdcts=vcloudBrands.objects.get(brand=j['brand__brand'])
            print(prdcts.brand)
            print(prdcts.logo.url)
            if(prdcts):
                print("Haiiii")
                cost=subgetvcloudproductcost(j['brand__brand'],username)
                data={'brand':prdcts.id,'brand__brand':prdcts.brand,'brand__id':prdcts.id,'brand__denomination':prdcts.denomination,'brand__logo':prdcts.logo.url,'barnd__description':prdcts.description,'brand__currency':prdcts.currency,'brand__category':prdcts.category,'cost':cost}
                print(data)
                brandlist.append(data)
        resellers = UserData.objects.filter(postId="Sub_Reseller",sponserId=request.session["user"])
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"reseller/vcloud/assignVcloudBrands.html",{'brands':brands,'products':brandlist,'resellers':resellers,'user':userdetails})
        #return render(request,"reseller/vcloud/assignVcloudBrands.html",{'brands':brands,'products':list(db),'resellers':resellers,'user':userdetails})
    else:
        return redirect(LoginPage)


def resellerviewbrands(request):
    if request.session.has_key("user"):
        username = request.session["user"]
        vcdprod=vcloudBrands.objects.all()
        resultlist=list()
        statuslist=list()
        for i in vcdprod:
            vca=vcloudAssignments.objects.filter(assignedto=username,brand__brand=i.brand)
            if not vca:
                statuslist.append(False)
            else:
                statuslist.append(True)
        vcd=list(vcdprod)
        print(vcd)
        print(statuslist)
        #print(data)
        ldb=zip(vcd,statuslist)
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"reseller/vcloud/viewBrands.html",{'pdcts':list(ldb),'user':userdetails})
    else:
        return redirect(LoginPage)

def buy_vcloud_brands(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            username=request.session["user"]
            brand = request.POST.get('brandid', None)
            quantity = request.POST.get('quantity', None)
            amt = request.POST.get('amt', None)
            branddet=vcloudBrands.objects.get(brand=brand)
            userdet=UserData.objects.get(username=request.session["user"])
            #checkqty = vcloudProducts.objects.filter(brand__brand=brand, status=True).exclude(productstatus=1).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('productcount')
            ctime=datetime.now()
            time = timedelta(minutes = 5)
            now_minus_5 = ctime - time
            checkqty=vcloudProducts.objects.filter(Q(brand__brand=brand) & Q(status=True) & (Q(sdate__isnull=True) | Q(sdate__lte=now_minus_5))).values('brand').annotate(productcount=Count('brand')).values('productcount')
            print(checkqty)
            needamt=0;
            result=list()
            content=dict()
            licheckqty=list(checkqty)
            brand_id=0
            deno=0
            if(licheckqty[0]['productcount'] >= int(quantity)):
                usertype=''
                marginlist=list()
                margins=0
                count=0;
                flag=True
                prdct_id=''
                mllist=list()
                sponserlist=list()
                prdctdet = vcloudProducts.objects.filter(Q(brand__brand=brand) & Q(status=True) & (Q(sdate__isnull=True) | Q(sdate__lte=now_minus_5)))[:int(quantity)]
                ctime = datetime.now()
                for i in prdctdet:
                    i.productstatus=1
                    i.suser = userdet
                    i.sdate = ctime
                    i.save()
                count=0
                admin=''
                while(True):
                    userdet2=UserData.objects.filter(username=username).values('sponserId','postId','balance')
                    margindet=vcloudAssignments.objects.filter(assignedto=username,brand__brand=brand).values('margin')
                    if(userdet2[0]['postId']=="Admin"):
                        admin=username
                        break;
                    else:
                        cost=Decimal(amt)
                        prdctcost = (cost*Decimal(quantity))-(Decimal(margins)*Decimal(quantity))
                        margins=margins+Decimal(margindet[0]['margin'])
                        #print(prdctcost)
                        #print(cost)
                        if(userdet2[0]['balance']>=prdctcost):
                            data={'margin':margindet[0]['margin'],'balance':userdet2[0]['balance'],'username':username,'prdctcost':prdctcost}
                            marginlist.append(data)
                            mllist.append(margindet[0]['margin'])
                            sponserlist.append(username)
                        else:
                            flag=False
                            print(flag)
                            break;
                    username=userdet2[0]['sponserId']
                if(flag):
                    try:
                        prdctcddet=vcloudProducts.objects.filter(brand__brand=brand,status=True,productstatus=1,suser=userdet,sdate=ctime)[:int(quantity)]
                        for h in prdctcddet:
                            h.status=False
                            h.save()
                            #print(h.username)
                            brand_id=h.brand.id
                            deno=h.brand.denomination
                            prdct_id=prdct_id+""+str(h.id)+","
                            res={"productid":h.id,"carduname":h.username,'brand':h.brand.brand,'brand_logo':h.brand.logo.url,'password':h.password,'status':h.status,'suser':username,'sdate':h.sdate}
                            result.append(res)

                        ml=marginlist[::-1]
                        for k in ml:
                            uname = k['username']
                            margin = k['margin']
                            balance = k['balance']
                            pcost = k['prdctcost']
                            cb=Decimal(balance)-Decimal(pcost)
                            userd=UserData.objects.get(username=uname)
                            userd.balance=cb
                            userd.save()
                        mllen = len(mllist)
                        vcrep=vcloudtransactions()
                        vcrep.saleduser = userdet
                        vcrep.brand = brand
                        vcrep.type = "Vcloud"
                        vcrep.brand_id = brand_id
                        vcrep.product_id = prdct_id
                        vcrep.quantity = quantity
                        vcrep.amount = amt
                        vcrep.rtype = "Web"
                        vcrep.denominations = deno
                        ms = mllist[::-1]
                        mu = sponserlist[::-1]
                        print(ms)
                        print(admin)
                        ad=UserData.objects.get(username=admin)
                        if(mllen==1):
                            vcrep.margin1=ms[0]
                            vcrep.sponser1=ad
                            vcrep.sponser2=UserData.objects.get(username=sponserlist[0])
                        elif(mllen==2):
                            vcrep.margin1=ms[0]
                            vcrep.margin2=ms[1]
                            vcrep.sponser1=ad
                            vcrep.sponser2=UserData.objects.get(username=sponserlist[1])
                            vcrep.sponser3=UserData.objects.get(username=sponserlist[0])
                        else:
                            vcrep.margin1=ms[0]
                            vcrep.margin2=ms[1]
                            vcrep.margin3=ms[2]
                            vcrep.sponser1=ad
                            vcrep.sponser2=UserData.objects.get(username=sponserlist[2])
                            vcrep.sponser3=UserData.objects.get(username=sponserlist[1])
                            vcrep.sponser4=UserData.objects.get(username=sponserlist[0])
                        vcrep.save()
                        obj = vcloudtransactions.objects.latest('id')
                        print(obj.id)
                        content["data"] = result
                        content["res_status"]="success"
                        content["trid"]=obj.id
                    except:
                        content["res_status"]="Failed"
                else:
                    for i in prdctdet:
                        i.suser=None
                        i.save()
                    content["res_status"]="Failed"
            return JsonResponse(content,safe=False)
        else:
            return redirect(resellervcloudStore)
    else:
        return redirect(LoginPage)

def printLayout(request):
    return render(request,"reseller/printLayout.html")

def downloadvcloudresellercards(request,trid):
    print(trid)
    trdet=vcloudtransactions.objects.get(id=trid)
    print(trdet)
    image="media/img/card.png"
    img = Image.open(image)
    draw = ImageDraw.Draw(img)
    fontpath = os.path.join(settings.BASE_DIR, "static/pfont/sans_serif.ttf")
    print(fontpath)
    font = ImageFont.truetype(fontpath, 16)
    type=trdet.type
    productid=trdet.product_id
    result = productid.rstrip(',')
    pdid = result.split(',')
    for i in pdid:
        pddet=vcloudProducts.objects.get(id=i)
        imagelogo=pddet.brand.logo.url
        str=imagelogo.replace("%20", " ")
        print(str)
        logo = str.lstrip('/')
        print(image)
        print(logo)
        draw.text((100, 200),"Owner    : "+pddet.suser.name,(0,0,0),font=font)
        draw.text((100, 230),"Brand    : "+pddet.brand.brand,(0,0,0),font=font)
        draw.text((100, 260),"Username : "+pddet.username,(0,0,0),font=font)
        draw.text((100, 290),"Password : "+pddet.password,(0,0,0),font=font)
        img.save('media/img/sample-out.png')
        dimage = Image.open(os.path.join(settings.MEDIA_ROOT, "img/sample-out.png"))
        print(dimage)

        filename = dimage.filename
        print(filename)
        wrapper = FileWrapper(open(filename,'rb'))
        content_type = mimetypes.guess_type(filename)[0]
        print(content_type)
        response = HttpResponse(wrapper, content_type='content_type')
        response['Content-Disposition'] = "attachment; filename=card.png"
        return response
    return redirect(resellervcloudStore)

def downloaddcardresellercards(request,trid):
    print(trid)
    trdet=vcloudtransactions.objects.get(id=trid)
    print(trdet)
    image="media/img/card.png"
    img = Image.open(image)
    draw = ImageDraw.Draw(img)
    fontpath = os.path.join(settings.BASE_DIR, "static/pfont/sans_serif.ttf")
    print(fontpath)
    font = ImageFont.truetype(fontpath, 16)
    type=trdet.type
    productid=trdet.product_id
    result = productid.rstrip(',')
    pdid = result.split(',')
    for i in pdid:
        pddet=datacardproducts.objects.get(id=i)
        print(image)
        draw.text((100, 200),"Owner    : "+pddet.suser.name,(0,0,0),font=font)
        draw.text((100, 230),"Brand    : "+pddet.brand.brand,(0,0,0),font=font)
        draw.text((100, 260),"Username : "+pddet.username,(0,0,0),font=font)
        img.save('media/img/sample-out.png')
        dimage = Image.open(os.path.join(settings.MEDIA_ROOT, "img/sample-out.png"))
        print(dimage)
        filename = dimage.filename
        print(filename)
        wrapper = FileWrapper(open(filename,'rb'))
        content_type = mimetypes.guess_type(filename)[0]
        print(content_type)
        response = HttpResponse(wrapper, content_type='content_type')
        response['Content-Disposition'] = "attachment; filename=card.png"
        return response
    return redirect(resellerdcardstore)

def downloaddcardsubresellercards(request,trid):
    print(trid)
    trdet=vcloudtransactions.objects.get(id=trid)
    print(trdet)
    image="media/img/card.png"
    img = Image.open(image)
    draw = ImageDraw.Draw(img)
    fontpath = os.path.join(settings.BASE_DIR, "static/pfont/sans_serif.ttf")
    print(fontpath)
    font = ImageFont.truetype(fontpath, 16)
    type=trdet.type
    productid=trdet.product_id
    result = productid.rstrip(',')
    pdid = result.split(',')
    for i in pdid:
        pddet=datacardproducts.objects.get(id=i)
        print(image)
        draw.text((100, 200),"Owner    : "+pddet.suser.name,(0,0,0),font=font)
        draw.text((100, 230),"Brand    : "+pddet.brand.brand,(0,0,0),font=font)
        draw.text((100, 260),"Username : "+pddet.username,(0,0,0),font=font)
        img.save('media/img/sample-out.png')
        dimage = Image.open(os.path.join(settings.MEDIA_ROOT, "img/sample-out.png"))
        print(dimage)
        filename = dimage.filename
        print(filename)
        wrapper = FileWrapper(open(filename,'rb'))
        content_type = mimetypes.guess_type(filename)[0]
        print(content_type)
        response = HttpResponse(wrapper, content_type='content_type')
        response['Content-Disposition'] = "attachment; filename=card.png"
        return response
    return redirect(subresellerdcardstore)

def downloaddcardusercards(request,trid):
    print(trid)
    trdet=vcloudtransactions.objects.get(id=trid)
    print(trdet)
    image="media/img/card.png"
    img = Image.open(image)
    draw = ImageDraw.Draw(img)
    fontpath = os.path.join(settings.BASE_DIR, "static/pfont/sans_serif.ttf")
    print(fontpath)
    font = ImageFont.truetype(fontpath, 16)
    type=trdet.type
    productid=trdet.product_id
    result = productid.rstrip(',')
    pdid = result.split(',')
    for i in pdid:
        pddet=datacardproducts.objects.get(id=i)
        print(image)
        draw.text((100, 200),"Owner    : "+pddet.suser.name,(0,0,0),font=font)
        draw.text((100, 230),"Brand    : "+pddet.brand.brand,(0,0,0),font=font)
        draw.text((100, 260),"Username : "+pddet.username,(0,0,0),font=font)
        img.save('media/img/sample-out.png')
        dimage = Image.open(os.path.join(settings.MEDIA_ROOT, "img/sample-out.png"))
        print(dimage)
        filename = dimage.filename
        print(filename)
        wrapper = FileWrapper(open(filename,'rb'))
        content_type = mimetypes.guess_type(filename)[0]
        print(content_type)
        response = HttpResponse(wrapper, content_type='content_type')
        response['Content-Disposition'] = "attachment; filename=card.png"
        return response
    return redirect(userdcardstore)

def downloadvcloudsubresellercards(request,trid):
    print(trid)
    trdet=vcloudtransactions.objects.get(id=trid)
    print(trdet)
    image="media/img/card.png"
    img = Image.open(image)
    draw = ImageDraw.Draw(img)
    fontpath = os.path.join(settings.BASE_DIR, "static/pfont/sans_serif.ttf")
    print(fontpath)
    font = ImageFont.truetype(fontpath, 16)
    type=trdet.type
    productid=trdet.product_id
    result = productid.rstrip(',')
    pdid = result.split(',')
    for i in pdid:
        pddet=vcloudProducts.objects.get(id=i)
        imagelogo=pddet.brand.logo.url
        str=imagelogo.replace("%20", " ")
        print(str)
        logo = str.lstrip('/')
        print(image)
        print(logo)
        draw.text((100, 200),"Owner    : "+pddet.suser.name,(0,0,0),font=font)
        draw.text((100, 230),"Brand    : "+pddet.brand.brand,(0,0,0),font=font)
        draw.text((100, 260),"Username : "+pddet.username,(0,0,0),font=font)
        draw.text((100, 290),"Password : "+pddet.password,(0,0,0),font=font)
        img.save('media/img/sample-out.png')
        dimage = Image.open(os.path.join(settings.MEDIA_ROOT, "img/sample-out.png"))
        print(dimage)

        filename = dimage.filename
        print(filename)
        wrapper = FileWrapper(open(filename,'rb'))
        content_type = mimetypes.guess_type(filename)[0]
        print(content_type)
        response = HttpResponse(wrapper, content_type='content_type')
        response['Content-Disposition'] = "attachment; filename=card.png"
        return response
    return redirect(subresellervcloudStore)

def downloadvcloudusercards(request,trid):
    print(trid)
    trdet=vcloudtransactions.objects.get(id=trid)
    print(trdet)
    image="media/img/card.png"
    img = Image.open(image)
    draw = ImageDraw.Draw(img)
    fontpath = os.path.join(settings.BASE_DIR, "static/pfont/sans_serif.ttf")
    print(fontpath)
    font = ImageFont.truetype(fontpath, 16)
    type=trdet.type
    productid=trdet.product_id
    result = productid.rstrip(',')
    pdid = result.split(',')
    for i in pdid:
        pddet=vcloudProducts.objects.get(id=i)
        imagelogo=pddet.brand.logo.url
        str=imagelogo.replace("%20", " ")
        print(str)
        logo = str.lstrip('/')
        print(image)
        print(logo)
        draw.text((100, 200),"Owner    : "+pddet.suser.name,(0,0,0),font=font)
        draw.text((100, 230),"Brand    : "+pddet.brand.brand,(0,0,0),font=font)
        draw.text((100, 260),"Username : "+pddet.username,(0,0,0),font=font)
        draw.text((100, 290),"Password : "+pddet.password,(0,0,0),font=font)
        img.save('media/img/sample-out.png')
        dimage = Image.open(os.path.join(settings.MEDIA_ROOT, "img/sample-out.png"))
        print(dimage)

        filename = dimage.filename
        print(filename)
        wrapper = FileWrapper(open(filename,'rb'))
        content_type = mimetypes.guess_type(filename)[0]
        print(content_type)
        response = HttpResponse(wrapper, content_type='content_type')
        response['Content-Disposition'] = "attachment; filename=card.png"
        return response
    return redirect(uservcloudStore)

def downloadrcardresellercards(request,trid):
    print(trid)
    trdet=vcloudtransactions.objects.get(id=trid)
    print(trdet)
    image="media/img/card.png"
    img = Image.open(image)
    draw = ImageDraw.Draw(img)
    fontpath = os.path.join(settings.BASE_DIR, "static/pfont/sans_serif.ttf")
    print(fontpath)
    font = ImageFont.truetype(fontpath, 16)
    type=trdet.type
    productid=trdet.product_id
    result = productid.rstrip(',')
    pdid = result.split(',')
    for i in pdid:
        pddet=rcardProducts.objects.get(id=i)
        print(image)
        draw.text((100, 200),"Owner    : "+pddet.suser.name,(0,0,0),font=font)
        draw.text((100, 230),"Brand    : "+pddet.brand.brand,(0,0,0),font=font)
        draw.text((100, 260),"Username : "+pddet.username,(0,0,0),font=font)
        img.save('media/img/sample-out.png')
        dimage = Image.open(os.path.join(settings.MEDIA_ROOT, "img/sample-out.png"))
        print(dimage)
        filename = dimage.filename
        print(filename)
        wrapper = FileWrapper(open(filename,'rb'))
        content_type = mimetypes.guess_type(filename)[0]
        print(content_type)
        response = HttpResponse(wrapper, content_type='content_type')
        response['Content-Disposition'] = "attachment; filename=card.png"
        return response
    return redirect(resellerrcardstore)

def downloadrcardsubresellercards(request,trid):
    print(trid)
    trdet=vcloudtransactions.objects.get(id=trid)
    print(trdet)
    image="media/img/card.png"
    img = Image.open(image)
    draw = ImageDraw.Draw(img)
    fontpath = os.path.join(settings.BASE_DIR, "static/pfont/sans_serif.ttf")
    print(fontpath)
    font = ImageFont.truetype(fontpath, 16)
    type=trdet.type
    productid=trdet.product_id
    result = productid.rstrip(',')
    pdid = result.split(',')
    for i in pdid:
        pddet=rcardProducts.objects.get(id=i)
        print(image)
        draw.text((100, 200),"Owner    : "+pddet.suser.name,(0,0,0),font=font)
        draw.text((100, 230),"Brand    : "+pddet.brand.brand,(0,0,0),font=font)
        draw.text((100, 260),"Username : "+pddet.username,(0,0,0),font=font)
        img.save('media/img/sample-out.png')
        dimage = Image.open(os.path.join(settings.MEDIA_ROOT, "img/sample-out.png"))
        print(dimage)
        filename = dimage.filename
        print(filename)
        wrapper = FileWrapper(open(filename,'rb'))
        content_type = mimetypes.guess_type(filename)[0]
        print(content_type)
        response = HttpResponse(wrapper, content_type='content_type')
        response['Content-Disposition'] = "attachment; filename=card.png"
        return response
    return redirect(subresellerrcardstore)

def downloadrcardusercards(request,trid):
    print(trid)
    trdet=vcloudtransactions.objects.get(id=trid)
    print(trdet)
    image="media/img/card.png"
    img = Image.open(image)
    draw = ImageDraw.Draw(img)
    fontpath = os.path.join(settings.BASE_DIR, "static/pfont/sans_serif.ttf")
    print(fontpath)
    font = ImageFont.truetype(fontpath, 16)
    type=trdet.type
    productid=trdet.product_id
    result = productid.rstrip(',')
    pdid = result.split(',')
    for i in pdid:
        pddet=rcardProducts.objects.get(id=i)
        print(image)
        draw.text((100, 200),"Owner    : "+pddet.suser.name,(0,0,0),font=font)
        draw.text((100, 230),"Brand    : "+pddet.brand.brand,(0,0,0),font=font)
        draw.text((100, 260),"Username : "+pddet.username,(0,0,0),font=font)
        img.save('media/img/sample-out.png')
        dimage = Image.open(os.path.join(settings.MEDIA_ROOT, "img/sample-out.png"))
        print(dimage)
        filename = dimage.filename
        print(filename)
        wrapper = FileWrapper(open(filename,'rb'))
        content_type = mimetypes.guess_type(filename)[0]
        print(content_type)
        response = HttpResponse(wrapper, content_type='content_type')
        response['Content-Disposition'] = "attachment; filename=card.png"
        return response
    return redirect(userrcardstore)

#________________DCARD_______________

def resellerDcardDashboard(request):
    if request.session.has_key("user"):
        last_month = datetime.today() - timedelta(days=1)
        username = request.session["user"]
        #print(last_month)
        reseller = UserData.objects.filter(sponserId=username,postId="Sub_Reseller")
        #print(reseller)
        resellerlist=list()
        for i in reseller:
            resellerdata={'username':i.username,'name':i.name}
            resellerlist.append(resellerdata)
        username = request.session["user"]
        type = request.session["usertype"]
        try:
            user = UserData.objects.get(username = username, postId = type)
        except UserData.DoesNotExist:
            return redirect(LoginPage)
        userdetails = UserData.objects.get(username=request.session["user"])
        username=request.session["user"]
        last_month = datetime.today() - timedelta(days=1)
        vcloudtxns = vcloudtransactions.objects.filter(date__gte=last_month,sponser2__username=username,type="Dcard").order_by('-date')
        content=list()
        topuser=list()
        noofrecords=0
        productsum =0
        quantitysum =0
        profitsum =0
        count=0
        for i in vcloudtxns:
            count=count+1
            cost=i.denominations+i.margin1
            productsum=productsum+(cost*i.quantity)
            quantitysum=quantitysum+i.quantity
            if(i.saleduser.username==username):
                profit=0
                #data3={'user':i.sponser2.name,'amount':(i.denominations*i.quantity)}
                data={"id":i.id,"saleduser":i.sponser2.name,"role":i.sponser2.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                content.append(data)
                profitsum = profitsum+profit
            else:
                profit=i.margin2*i.quantity
                data3={'user':i.sponser3.name,'amount':(cost*i.quantity)}
                topuser.append(data3)
                data={"id":i.id,"saleduser":i.sponser3.name,"role":i.sponser3.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                content.append(data)
                profitsum = profitsum+profit
        box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum,'noofrecords':count}
        brand = datacardAssignments.objects.filter(assignedto=username).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description','margin')
        product=list()
        for i in brand:
            pd=datacardproducts.objects.filter(brand=i['brand__id'], status=True).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
            lpd=list(pd)
            count=0
            if not lpd:
                pass;
                #break;
                #print("Haiii")
            else:
                username=request.session["user"]
                productcost=Decimal(lpd[0]['brand__denomination'])
                print(productcost)
                while(True):
                    userdet2=UserData.objects.filter(username=username).values('sponserId','postId')
                    print(userdet2)
                    margindet=datacardAssignments.objects.filter(assignedto=username,brand__brand=i['brand__brand']).values('margin')
                    if(userdet2[0]['postId']=="Admin"):
                        break;
                    else:
                        print(margindet[0]['margin'])
                        productcost = Decimal(productcost)+Decimal(margindet[0]['margin'])
                        print(productcost)
                        username=userdet2[0]['sponserId']
                    count=int(count)+1
                data={"brand":lpd[0]['brand__brand'],'rate':productcost}
                product.append(data)
                #print(content)

        list3=list()
        sorted_users = sorted(topuser, key=itemgetter('user'))

        for key, group in itertools.groupby(sorted_users, key=lambda x:x['user']):
            amountsum=0
            for g in group:
                amountsum=amountsum+g["amount"]
                #print(amountsum)
            data5={'user':key,'amount':amountsum}
            list3.append(data5)
        return render(request,"reseller/dcard/dashboard-dcard.html",{'filterform':dcardDashboardfilter,'reseller':resellerlist,'recenttransactions':content,'products':product,'user':user,'topuser':list3,'last_month':last_month,'boxval':box_data})
    else:
        return redirect(LoginPage)

def filterresellerDcardDashboard(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = dcardDashboardfilter(request.POST or None)
            print(form.errors)
            if form.is_valid():
                currentuser=request.session["user"]
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                usertype=form.cleaned_data.get("usertype")
                uuusername=form.cleaned_data.get("username")
                #mffromdate=datetime.strptime(fromdate, '%b %d %Y %I:%M%p')
                #print(type(fromdate))
                #print(fromdate.strftime("%B %d, %Y"))
                last_month=fromdate.strftime("%B %d, %I:%M %p")+" To "+todate.strftime("%B %d, %I:%M %p")
                reseller = UserData.objects.filter(sponserId=currentuser,postId="Sub_Reseller")
                #print(reseller)
                resellerlist=list()
                for i in reseller:
                    resellerdata={'username':i.username,'name':i.name}
                    resellerlist.append(resellerdata)
                #print(username)
                userdetails = UserData.objects.get(username=request.session["user"])
                vcloudtxns = vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate,sponser2__username=currentuser,type="Dcard",sponser3__username=uuusername).order_by('-date')
                content=list()
                topuser=list()
                noofrecords=0
                productsum =0
                quantitysum =0
                profitsum =0
                count=0
                for i in vcloudtxns:
                    count=count+1
                    cost=i.denominations+i.margin1
                    productsum=productsum+(cost*i.quantity)
                    quantitysum=quantitysum+i.quantity
                    if(i.saleduser.username==username):
                        profit=0
                        #data3={'user':i.sponser2.name,'amount':(i.denominations*i.quantity)}
                        data={"id":i.id,"saleduser":i.sponser2.name,"role":i.sponser2.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                        content.append(data)
                        profitsum = profitsum+profit
                    else:
                        profit=i.margin2*i.quantity
                        data3={'user':i.sponser3.name,'amount':(cost*i.quantity)}
                        topuser.append(data3)
                        data={"id":i.id,"saleduser":i.sponser3.name,"role":i.sponser3.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                        content.append(data)
                        profitsum = profitsum+profit
                box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum,'noofrecords':count}
                brand = datacardAssignments.objects.filter(assignedto=currentuser).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description','margin')
                product=list()
                print(brand)
                for i in brand:
                    print(i['brand__id'])
                    pd=datacardproducts.objects.filter(brand=i['brand__id'],status=True).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
                    lpd=list(pd)
                    count=0
                    if not lpd:
                        pass
                    else:
                        username=request.session["user"]
                        productcost=Decimal(lpd[0]['brand__denomination'])
                        print(productcost)
                        while(True):
                            userdet2=UserData.objects.filter(username=username).values('sponserId','postId')
                            print(userdet2)
                            margindet=datacardAssignments.objects.filter(assignedto=username,brand__brand=i['brand__brand']).values('margin')
                            if(userdet2[0]['postId']=="Admin"):
                                break;
                            else:
                                print(margindet[0]['margin'])
                                productcost = Decimal(productcost)+Decimal(margindet[0]['margin'])
                                print(productcost)
                                username=userdet2[0]['sponserId']
                            count=int(count)+1
                        data={"brand":lpd[0]['brand__brand'],'rate':productcost}
                        product.append(data)
                        #print(content)
                print(product)
                list3=list()
                sorted_users = sorted(topuser, key=itemgetter('user'))

                for key, group in itertools.groupby(sorted_users, key=lambda x:x['user']):
                    amountsum=0
                    for g in group:
                        amountsum=amountsum+g["amount"]
                        #print(amountsum)
                    data5={'user':key,'amount':amountsum}
                    list3.append(data5)
                return render(request,"reseller/dcard/dashboard-dcard.html",{'filterform':vcloudDashboardfilter,'reseller':resellerlist,'recenttransactions':content,'products':product,'user':userdetails,'topuser':list3,'last_month':last_month,'boxval':box_data})
            else:
                return redirect(resellerDcardDashboard)
        else:
            return(resellerDcardDashboard)
    else:
        return redirect(LoginPage)

def resellerprofiledcard(request):
    if request.session.has_key("user"):
        user = request.session["user"]
        userDet = UserData.objects.get(username=user)
        return render(request,"reseller/dcard/editProfile.html",{'user':userDet})
    else:
        return redirect(LoginPage)

def reselleraddResellerDcard(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"reseller/dcard/addReseller.html",{'form':AddUserDataForm,'user':userdetails})
    else:
        return redirect(LoginPage)

def reselleraddUserDcard(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"reseller/dcard/addUser.html",{'form':AddUserDataForm,'user':userdetails})
    else:
        return redirect(LoginPage)

def resellerviewResellerDcard(request):
    if request.session.has_key("user"):
        resellers = UserData.objects.filter(sponserId=request.session["user"],postId="Sub_Reseller")
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"reseller/dcard/viewResellers.html",{'resellers':resellers,'user':userdetails})
    else:
        return redirect(LoginPage)

def resellerviewUserDcard(request):
    if request.session.has_key("user"):
        user = request.session["user"]
        resellers = UserData.objects.filter(postId="User",sponserId=user)
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"reseller/dcard/viewUser.html",{'resellers':resellers,'user':userdetails})
    else:
        return redirect(LoginPage)

def resellerbalanceTransferDcard(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        bthist=balanceTransactionReport.objects.filter(source=userdetails,category="BT").order_by('-date')
        #print(bthist)
        return render(request,"reseller/dcard/balanceTransfer.html",{'bthist':bthist,'user':userdetails})
    else:
        return redirect(LoginPage)

def reselleraddPaymentDcard(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        phist=fundTransactionReport.objects.filter(source=userdetails).order_by('-date')
        return render(request,"reseller/dcard/addPayment.html",{'phist':phist})
    else:
        return redirect(LoginPage)

def resellerdatacardreport(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        username=request.session["user"]
        last_month = datetime.today() - timedelta(days=1)
        vcloudtxns = vcloudtransactions.objects.filter(date__gte=last_month,sponser2__username=username).order_by('-date')
        #vcloudtxns = vcloudtransactions.objects.all().order_by('-date')
        reseller=UserData.objects.filter(sponserId=username,postId="Reseller")
        resellerlist=list()
        vcbrand=vcloudBrands.objects.all()
        vcbrandlist=list()
        for b in vcbrand:
            branddata={'brand':b.brand}
            vcbrandlist.append(branddata)

        for i in reseller:
            resellerdata={'username':i.username,'name':i.name}
            resellerlist.append(resellerdata)
        content=list()
        noofrecords=0
        productsum =0
        quantitysum =0
        profitsum =0
        cost=0
        for i in vcloudtxns:
            cost=i.denominations+i.margin1
            productsum=productsum+(cost*i.quantity)
            quantitysum=quantitysum+i.quantity
            if(i.saleduser.username==username):
                profit=0
                data={"id":i.id,"saleduser":i.sponser2.name,"role":i.sponser2.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                content.append(data)
                profitsum = profitsum+profit
            else:
                profit=(i.margin2*i.quantity)
                data={"id":i.id,"saleduser":i.sponser3.name,"role":i.sponser3.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                content.append(data)
                profitsum = profitsum+profit
        box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum}
        return render(request,"reseller/dcard/dcardreport.html",{'filterform':vcloudreportfilterform,'products':content,'user':userdetails,'reseller':resellerlist, 'brand':vcbrandlist,'box':box_data,'date':last_month})
    else:
        return redirect(LoginPage)

def filterresellerdcard_report(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            form = vcloudreportfilterform(request.POST or None)
            print(form.errors)
            if form.is_valid():
                username=request.session["user"]
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                usertype=form.cleaned_data.get("usertype")
                fusername=form.cleaned_data.get("username")
                type=form.cleaned_data.get("type")
                brand=form.cleaned_data.get("brand")
                fuser=''
                if(fusername!='All'):
                    filterdata=UserData.objects.get(username=fusername)
                    fuser=filterdata.name
                else:
                    fuser=fusername
                filter={'ffdate':fromdate,'ttdate':todate,'fuser':fuser}
                #print(brand,fusername)
                reseller=UserData.objects.filter(sponserId=username,postId="Sub_Reseller")
                resellerlist=list()
                userdetails = UserData.objects.get(username=request.session["user"])
                vcbrand=vcloudBrands.objects.all()
                vcbrandlist=list()
                for b in vcbrand:
                    branddata={'brand':b.brand}
                    vcbrandlist.append(branddata)

                for i in reseller:
                    resellerdata={'username':i.username,'name':i.name}
                    resellerlist.append(resellerdata)

                content=list()
                noofrecords = 0
                productsum = 0
                quantitysum = 0
                profitsum = 0
                vcloudtxns=vcloudtransactions()
                try:
                    print(usertype)
                    print(fusername)
                    print(type)
                    print(brand)
                    if(usertype=="All" and fusername=="All" and type=="All" and brand=="All"):
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser2__username=username).order_by('-date')
                        print("One")
                    elif(usertype=="All" and fusername=="All" and type=="All" and brand !="All"):
                        print("TWo")
                        vcloudtxns==vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser2__username=username, brand=brand).order_by('-date')
                    elif(usertype=="All" and fusername=="All" and type !="All" and brand =="All"):
                        print("Three")
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser2__username=username, type=type).order_by('-date')
                    elif(usertype=="All" and fusername=="All" and type !="All" and brand !="All"):
                        print("four")
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser2__username=username, brand=brand).order_by('-date')
                    elif(usertype=="All" and fusername!="All" and type !="All" and brand !="All"):
                        print('five')
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, type=type, sponser2__username=username, sponser3__username=fusername, brand=brand).order_by('-date')
                    elif(usertype !="All" and fusername =="All" and type =="All" and brand !="All"):
                        print('Six')
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser3__postId=usertype, sponser2__username=username).order_by('-date')
                    elif(usertype !="All" and fusername =="All" and type =="All" and brand =="All"):
                        print('Six')
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser2__username=username, sponser3__postId=usertype).order_by('-date')
                    elif(usertype =="All" and fusername !="All" and type =="All" and brand =="All"):
                        print('Six')
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser2__username=username, sponser3__username=fusername).order_by('-date')
                    elif(usertype !="All" and fusername !="All" and type =="All" and brand =="All"):
                        print('Six')
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser2__username=username, sponser3__username=fusername).order_by('-date')
                    else:
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser2__username=username, sponser3__username=fusername,brand=brand).order_by('-date')
                    print(vcloudtxns)
                    for i in vcloudtxns:
                        cost=i.denominations+i.margin1
                        productsum=productsum+(cost*i.quantity)
                        quantitysum=quantitysum+i.quantity
                        if(i.saleduser.username==username):
                            profit=0
                            data={"id":i.id,"saleduser":i.sponser2.name,"role":i.sponser2.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                            content.append(data)
                            profitsum = profitsum+profit
                        else:
                            profit=(i.margin2*i.quantity)
                            data={"id":i.id,"saleduser":i.sponser3.name,"role":i.sponser3.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                            content.append(data)
                            profitsum = profitsum+profit
                except:
                    pass
                box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum}
                return render(request,"reseller/dcard/dcardreport.html",{'filterform':vcloudreportfilterform,'products':content,'user':userdetails,'reseller':resellerlist, 'brand':vcbrandlist,'box':box_data,'filter':filter})
            else:
                return redirect(resellerdatacardreport)
        else:
            return redirect(resellerdatacardreport)
    else:
        return redirect(LoginPage)

def resellerbTReportDcard(request):
    if request.session.has_key("user"):
        username = request.session["user"]
        userdetails = UserData.objects.get(username=request.session["user"])
        reseller = UserData.objects.filter(sponserId=username,postId="Sub_Reseller")
        fromsum = balanceTransactionReport.objects.filter(source=userdetails,category='BT').aggregate(Sum('amount'))
        tosum = balanceTransactionReport.objects.filter(destination=userdetails,category='BT').aggregate(Sum('amount'))
        bthist = balanceTransactionReport.objects.filter(source=userdetails).order_by("-date") | balanceTransactionReport.objects.filter(destination=userdetails).order_by("-date")
        return render(request,"reseller/dcard/balanceTransferReport.html",{'form':balancetransferfilterform,'reseller':reseller,'bthist':bthist,'fromsum':fromsum['amount__sum'],'tosum':tosum['amount__sum'],'user':userdetails})
    else:
        return redirect(LoginPage)

def filterresellerdcardbtreport(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            form = balancetransferfilterform(request.POST or None)
            print(form.errors)
            if form.is_valid():
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                usertype=form.cleaned_data.get("usertype")
                susername=form.cleaned_data.get("username")
                username=request.session["user"]
                #fuser=UserData.objects.get(username=susername)
                filter={'ffdate':fromdate,'ttdate':todate,'fuser':susername}
                userdetails = UserData.objects.get(username=request.session["user"])
                reseller = UserData.objects.filter(sponserId=username,postId="Sub_Reseller")
                fromsum=None
                tosum=None
                bthist=None
                try:
                    if(usertype == "Self"):
                        fromsum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails).aggregate(Sum('amount'))
                        tosum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdetails).aggregate(Sum('amount'))
                        bthist = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdetails)
                    elif(usertype == "All" and susername == "All"):
                        fromsum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails).aggregate(Sum('amount'))
                        tosum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdetails).aggregate(Sum('amount'))
                        bthist = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails)
                    elif(usertype!="All" and susername == "All"):
                        fromsum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__postId=usertype).aggregate(Sum('amount'))
                        tosum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdetails).aggregate(Sum('amount'))
                        bthist = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__postId=usertype)
                    else:
                        fromsum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__username=susername).aggregate(Sum('amount'))
                        tosum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdetails).aggregate(Sum('amount'))
                        bthist = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__username=susername)
                except:
                    pass
                return render(request,"reseller/dcard/balanceTransferReport.html",{'form':balancetransferfilterform,'reseller':reseller,'bthist':bthist,'fromsum':fromsum['amount__sum'],'tosum':tosum['amount__sum'],'user':userdetails,'filter':filter})
            else:
                return redirect(resellerbTReportDcard)
        else:
            return redirect(resellerbTReportDcard)
    else:
        return redirect(LoginPage)

def resellerpaymentReportDcard(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        reseller = UserData.objects.filter(sponserId=request.session["user"],postId="Sub_Reseller")
        phist = fundTransactionReport.objects.filter(source=userdetails).order_by('-date')|fundTransactionReport.objects.filter(destination=userdetails).order_by('-date')
        bsum = fundTransactionReport.objects.filter(source=userdetails).aggregate(Sum('amount'))
        return render(request,"reseller/dcard/paymentReport.html",{'form':paymentfilterform,'reseller':reseller,'phist':phist,'sum':bsum['amount__sum'],'user':userdetails})
    else:
        return redirect(LoginPage)

def filterresellerdcardpaymentreport(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            form = balancetransferfilterform(request.POST or None)
            print(form.errors)
            if form.is_valid():
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                usertype=form.cleaned_data.get("usertype")
                susername=form.cleaned_data.get("username")
                username = request.session["user"]
                filter={'ffdate':fromdate,'ttdate':todate,'fuser':susername}
                userdetails = UserData.objects.get(username=request.session["user"])
                reseller = UserData.objects.filter(sponserId=username,postId="Sub_Reseller")
                bsum=None
                phist=None
                try:
                    if(usertype == "Self" ):
                        bsum = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdetails).aggregate(Sum('amount'))
                        phist = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdetails)
                    elif(usertype == "All" and susername == "All"):
                        bsum = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails).aggregate(Sum('amount'))
                        phist = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails)
                        #print(phist)
                        #print("phist")
                    elif(usertype!="All" and susername == "All"):
                        #print(usertype)
                        bsum = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails).aggregate(Sum('amount'))
                        phist = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails, destination__postId=usertype)
                        #print("Haiii")
                    else:
                        bsum = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__username=susername).aggregate(Sum('amount'))
                        phist = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__username=susername)
                except Exception as e:
                    print(e)
                    pass
                return render(request,"reseller/dcard/paymentReport.html",{'form':paymentfilterform,'reseller':reseller,'phist':phist,'sum':bsum['amount__sum'],'user':userdetails,'filter':filter})
            else:
                return redirect(resellerpaymentReportDcard)
        else:
            return redirect(resellerpaymentReportDcard)
    else:
        return redirect(LoginPage)

def resellerassignDCardBrands(request):
    if request.session.has_key("user"):
        brands = datacardAssignments.objects.filter(assignedto=request.session["user"]).values('brand','brand__brand','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
        username = request.session["user"]
        bd=list(brands)
        prdcts=list()
        costs=list()
        for i in brands:
            prd=dcardBrands.objects.get(brand=i['brand__brand'])
            #prd=datacardproducts.objects.filter(brand__brand=i['brand__brand'], status=True).order_by('brand').values('brand').annotate(productcount=Count('brand')).values('brand','brand__brand','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
            #print(prd)
            if(prd):
                cost=getDatacardProductCost(username,i["brand__brand"])
                data={'brand__brand':prd.brand,'brand__logo':prd.logo.url,'brand__id':prd.id,'cost':cost,'brand__currency':prd.currency,'brand__description':prd.description}
                prdcts.append(data)
            else:
                pass;

        #print(pddata[0])
        resellers = UserData.objects.filter(postId="Sub_Reseller",sponserId=request.session["user"])
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"reseller/dcard/assignDcardbrand.html",{'brands':bd,'products':prdcts,'resellers':resellers,'user':userdetails})
    else:
        return redirect(LoginPage)

def resellerdcardstore(request):
    if request.session.has_key("user"):
        username=request.session["user"]
        user = UserData.objects.get(username=username)
        ads = adverisements.objects.filter(adtype="Image",usertype="Reseller",ctype="Dcard").order_by('-id')[:10]
        btnlist=list()
        dproducts = datacardAssignments.objects.filter(assignedto=username).order_by('brand').values('brand__brand','margin')
        for i in dproducts:
            buttons=(i["brand__brand"]).split(" ")
            if buttons[0] not in btnlist:
                btnlist.append(buttons[0])
        content=list()
        if(len(btnlist)!=0):
            dcardproducts = datacardAssignments.objects.filter(assignedto=username,brand__brand__contains=btnlist[0]).order_by('brand').values('brand__brand','margin')
            for i in dcardproducts:
                dcp=datacardproducts.objects.filter(brand__brand=i["brand__brand"],status=True).order_by('brand').values('brand').annotate(count=Count('brand')).values('count','brand__id','brand__brand','brand__description','brand__denomination','brand__logo','count','brand__currency')
                if(len(dcp)>0):
                    cost=getDatacardProductCost(username,dcp[0]["brand__brand"])
                    data={'brand__id':dcp[0]['brand__id'],'brand__brand':dcp[0]['brand__brand'],'brand__logo':dcp[0]['brand__logo'],'brand__description':dcp[0]['brand__description'],'brand__currency':dcp[0]['brand__currency'],'count':dcp[0]['count'],'cost':cost}
                    content.append(data)
                else:
                    pass
        else:
            pass
        print(content)
        return render(request,"reseller/dcard/datastore.html",{'dcardproducts':content,'btnlist':btnlist,'user':user,'ads':ads})
    else:
        return redirect(LoginPage)

def getDatacardProductCost(username,brand):
    prdcts=dcardBrands.objects.get(brand=brand)
    prdctcost=0
    if(prdcts):
        prdctcost = Decimal(prdcts.denomination)
        margins=0
        while(True):
            userdet = UserData.objects.filter(username=username).values('sponserId','postId')
            pdct = datacardAssignments.objects.filter(assignedto=username, brand__brand=brand).values('margin')
            if(pdct):
                if(userdet[0]['postId']=="Admin"):
                    break;
                else:
                    prdctcost = prdctcost+Decimal(pdct[0]['margin'])
                username=userdet[0]['sponserId']
            else:
                break;
    return prdctcost

def getRcardProductCost(username,brand):
    prdcts=rcardBrands.objects.get(brand=brand)
    prdctcost=0
    prdctcost = Decimal(prdcts.denomination)
    margins=0
    while(True):
        userdet = UserData.objects.filter(username=username).values('sponserId','postId')
        pdct = rcardAssignments.objects.filter(assignedto=username, brand__brand=brand).values('margin')
        if(userdet[0]['postId']=="Admin"):
            break;
        else:
            prdctcost = prdctcost+Decimal(pdct[0]['margin'])
        username=userdet[0]['sponserId']
    print(prdctcost)
    return prdctcost

def viewfiltereddatastore(brand):
    brands=datacardproducts.objects.filter(brand__brand__contains=brand,status=True).order_by('brand').values('brand').annotate(productcount=Count('brand')).values('productcount','brand__brand','brand__id','brand__description','brand__denomination','brand__logo','brand__currency')
    return brands

def resellerfilterdcardstore(request,brand):
    if request.session.has_key("user"):
        #print(brand)
        username=request.session["user"]
        user = UserData.objects.get(username=username)
        btnlist=list()
        ads = adverisements.objects.filter(adtype="Image",usertype="Reseller",ctype="Dcard").order_by('-id')[:10]
        dproducts = datacardAssignments.objects.filter(assignedto=username).order_by('brand').values('brand__brand','margin')
        for i in dproducts:
            buttons=(i["brand__brand"]).split(" ")
            if buttons[0] not in btnlist:
                btnlist.append(buttons[0])
        dcardproducts = datacardAssignments.objects.filter(assignedto=username,brand__brand__contains=brand).order_by('brand').values('brand__brand','margin')
        content=list()
        #print(buttons)
        for i in dcardproducts:
            dcp=datacardproducts.objects.filter(brand__brand=i["brand__brand"],status=True).order_by('brand').values('brand').annotate(count=Count('brand')).values('count','brand__id','brand__brand','brand__description','brand__denomination','brand__logo','count','brand__currency')
            if not dcp:
                pass
            else:
                cost=getDatacardProductCost(username,dcp[0]["brand__brand"])
                data={'brand__id':dcp[0]['brand__id'],'brand__brand':dcp[0]['brand__brand'],'brand__logo':dcp[0]['brand__logo'],'brand__description':dcp[0]['brand__description'],'brand__currency':dcp[0]['brand__currency'],'count':dcp[0]['count'],'cost':cost}
                content.append(data)
            print(content)
        return render(request,"reseller/dcard/datastore.html",{'dcardproducts':content,'btnlist':btnlist,'user':user,'ads':ads})
    else:
        return redirect(LoginPage)


def editresellerProfileDcard(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            user = request.session["user"]
            name = request.POST.get('name', None)
            address = request.POST.get('address', None)
            email = request.POST.get('email', None)
            mobileno = request.POST.get('mobileno', None)
            userDet = UserData.objects.get(username=user)
            userDet.name = name
            userDet.address = address
            userDet.email = email
            userDet.mobileno = mobileno
            userDet.save()
            messages.success(request, 'Successfully Updated')
            return redirect(resellerprofiledcard)
        else:
            messages.warning(request,'Internal Error Occured')
            return redirect(resellerprofiledcard)
    else:
        return redirect(LoginPage)

def resellerdcardsubmitReseller(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = AddUserDataForm(request.POST or None)
            print(form.errors)
            if form.is_valid():
                username=form.cleaned_data.get("username")
                password=form.cleaned_data.get("password")
                print(username)
                hashkey = username+password
                hash = hashlib.sha256(hashkey.encode()).hexdigest()
                sponser = request.session["user"]
                sponseruser=UserData.objects.get(username=sponser)
                Userdata=form.save(commit=False)
                Userdata.postId="Sub_Reseller"
                Userdata.sponserId = sponseruser
                Userdata.status = True
                Userdata.balance = 0
                Userdata.targetAmt = 0
                Userdata.rentalAmt = 0
                Userdata.dcard_status = True
                Userdata.rcard_status = True
                Userdata.password = hash
                Userdata.save()
                messages.success(request,'Successfully Added')
                return redirect(reselleraddResellerDcard)
            else:
                userdetails = UserData.objects.get(username=request.session["user"])
                messages.warning(request, 'Internal Error Occured')
                form = AddUserDataForm()
                return render(request,"reseller/dcard/addReseller.html",{'form':AddUserDataForm,'user':userdetails})
        else:
            userdetails = UserData.objects.get(username=request.session["user"])
            form = AddUserDataForm()
            return render(request,"reseller/dcard/addReseller.html",{'form':AddUserDataForm,'user':userdetails})
    else:
        return redirect(LoginPage)

def resellersubmitUser(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = AddUserDataForm(request.POST or None)
            print(form.errors)
            if form.is_valid():
                username=form.cleaned_data.get("username")
                password=form.cleaned_data.get("password")
                hashkey = username+password
                hash = hashlib.sha256(hashkey.encode()).hexdigest()
                sponser = request.session["user"]
                sponseruser=UserData.objects.get(username=sponser)
                Userdata=form.save(commit=False)
                Userdata.postId="User"
                Userdata.sponserId = sponseruser
                Userdata.status = True
                Userdata.balance = 0
                Userdata.targetAmt = 0
                Userdata.rentalAmt = 0
                Userdata.dcard_status = True
                Userdata.rcard_status = True
                Userdata.password = hash
                Userdata.save()
                messages.success(request, 'Successfully Added')
                return redirect(reselleraddUserDcard)
            else:
                userdetails = UserData.objects.get(username=request.session["user"])
                messages.warning(request, 'Internal Error Occured')
                form = AddUserDataForm()
                return render(request,"reseller/dcard/addUser.html",{'form':AddUserDataForm,'user':userdetails})
        else:
            userdetails = UserData.objects.get(username=request.session["user"])
            form = AddUserDataForm()
            return render(request,"reseller/dcard/addUser.html",{'form':AddUserDataForm,'user':username})
    else:
        return redirect(LoginPage)

def resellersubBalTransDcard(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            userType = request.POST.get('userType', None)
            user = request.POST.get('users', None)
            amount = request.POST.get('amount', None)
            userdet = UserData.objects.get(username=user)
            bal = userdet.balance
            newbal=bal+Decimal(amount)
            cdbal = userdet.targetAmt
            newcdbal = cdbal-Decimal(amount)
            userdet.targetAmt = newcdbal
            userdet.balance = newbal
            userdet.save()
            userdetails = UserData.objects.get(username=request.session["user"])
            btreport = balanceTransactionReport()
            btreport.source = userdetails
            btreport.destination = userdet
            btreport.category = "BT"
            btreport.pbalance = bal
            btreport.nbalance = newbal
            btreport.cramount = newcdbal
            btreport.amount = amount
            btreport.remarks = 'Added To Balance'
            btreport.save()
            messages.success(request, 'Successfully Updated The balance')
            return redirect(resellerbalanceTransferDcard)
            #userdata=UserData.objects.get(username=)
        else:
            messages.warning(request, 'Internal Error Occured')
            return redirect(resellerbalanceTransferDcard)
    else:
        return redirect(LoginPage)

def resellersubPayTrans(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            userType = request.POST.get('userType', None)
            user = request.POST.get('users', None)
            amount = request.POST.get('amount', None)
            remarks = request.POST.get('remarks', None)
            userdet = UserData.objects.get(username=user)
            obalance = userdet.targetAmt
            cdbal = userdet.targetAmt
            newcdbal = cdbal+Decimal(amount)
            userdet.targetAmt = newcdbal
            userdet.save()
            closeuser = UserData.objects.get(username=user)
            userdetails = UserData.objects.get(username=request.session["user"])
            ftreport=fundTransactionReport()
            ftreport.source = userdetails
            ftreport.destination = userdet
            ftreport.obalance = obalance
            ftreport.cbalance = closeuser.targetAmt
            ftreport.role = userType
            ftreport.amount = amount
            ftreport.balance = newcdbal
            ftreport.remarks = remarks
            ftreport.save()
            messages.success(request, 'Successfully Updated The balance')
            return redirect(resellervcloudaddPayment)
        else:
            messages.warning(request, 'Internal Error Occured')
            return redirect(resellervcloudaddPayment)
    else:
        return redirect(LoginPage)

def resellerdcardsubPayTrans(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            userType = request.POST.get('userType', None)
            user = request.POST.get('users', None)
            amount = request.POST.get('amount', None)
            remarks = request.POST.get('remarks', None)
            userdet = UserData.objects.get(username=user)
            obalance = userdet.targetAmt
            cdbal = userdet.targetAmt
            newcdbal = cdbal+Decimal(amount)
            userdet.targetAmt = newcdbal
            userdet.save()
            closeuser = UserData.objects.get(username=user)
            userdetails = UserData.objects.get(username=request.session["user"])
            ftreport=fundTransactionReport()
            ftreport.source = userdetails
            ftreport.destination = userdet
            ftreport.obalance = obalance
            ftreport.cbalance = closeuser.targetAmt
            ftreport.role = userType
            ftreport.amount = amount
            ftreport.balance = newcdbal
            ftreport.remarks = remarks
            ftreport.save()
            messages.success(request, 'Successfully Updated The balance')
            return redirect(reselleraddPaymentDcard)
        else:
            messages.warning(request, 'Internal Error Occured')
            return redirect(reselleraddPaymentDcard)
    else:
        return redirect(LoginPage)

def buy_datacard_brands(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            username=request.session["user"]
            brand = request.POST.get('brandid', None)
            quantity = request.POST.get('quantity', None)
            amt = request.POST.get('amt', None)
            branddet=dcardBrands.objects.get(brand=brand)
            userdet=UserData.objects.get(username=request.session["user"])
            ctime=datetime.now()
            time = timedelta(minutes = 5)
            now_minus_5 = ctime - time
            checkqty=datacardproducts.objects.filter(Q(brand__brand=brand) & Q(status=True) & (Q(sdate__isnull=True) | Q(sdate__lte=now_minus_5))).values('brand').annotate(productcount=Count('brand')).values('productcount')
            print(checkqty)
            needamt=0;
            result=list()
            content=dict()
            licheckqty=list(checkqty)
            brand_id=0
            deno=0
            if(licheckqty[0]['productcount'] >= int(quantity)):
                usertype=''
                marginlist=list()
                margins=0
                count=0;
                flag=True
                prdct_id=''
                mllist=list()
                sponserlist=list()
                prdctdet = datacardproducts.objects.filter(Q(brand__brand=brand) & Q(status=True) & (Q(sdate__isnull=True) | Q(sdate__lte=now_minus_5)))[:int(quantity)]
                ctime = datetime.now()
                for i in prdctdet:
                    i.productstatus=1
                    i.suser = userdet
                    i.sdate = ctime
                    i.save()
                count=0
                admin=''
                while(True):
                    userdet2=UserData.objects.filter(username=username).values('sponserId','postId','balance')
                    margindet=datacardAssignments.objects.filter(assignedto=username,brand__brand=brand).values('margin')
                    if(userdet2[0]['postId']=="Admin"):
                        admin=username
                        break;
                    else:
                        cost=Decimal(amt)
                        prdctcost = (cost*Decimal(quantity))-(Decimal(margins)*Decimal(quantity))
                        margins=margins+Decimal(margindet[0]['margin'])
                        #print(prdctcost)
                        #print(cost)
                        if(userdet2[0]['balance']>=prdctcost):
                            data={'margin':margindet[0]['margin'],'balance':userdet2[0]['balance'],'username':username,'prdctcost':prdctcost}
                            marginlist.append(data)
                            mllist.append(margindet[0]['margin'])
                            sponserlist.append(username)
                        else:
                            flag=False
                            print(flag)
                            break;
                    username=userdet2[0]['sponserId']
                if(flag):
                    try:
                        prdctcddet=datacardproducts.objects.filter(brand__brand=brand,status=True,productstatus=1,suser=userdet,sdate=ctime)[:int(quantity)]
                        for h in prdctcddet:
                            h.status=False
                            h.save()
                            brand_id=h.brand.id
                            deno=h.brand.denomination
                            prdct_id=prdct_id+""+str(h.id)+","
                            res={"productid":h.id,"carduname":h.username,'brand':h.brand.brand,'brand_logo':h.brand.logo.url, 'status':h.status,'suser':username,'sdate':h.sdate}
                            result.append(res)
                        ml=marginlist[::-1]
                        for k in ml:
                            uname = k['username']
                            margin = k['margin']
                            balance = k['balance']
                            pcost = k['prdctcost']
                            cb=Decimal(balance)-Decimal(pcost)
                            userd=UserData.objects.get(username=uname)
                            userd.balance=cb
                            userd.save()
                        mllen = len(mllist)
                        vcrep=vcloudtransactions()
                        vcrep.saleduser = userdet
                        vcrep.brand = brand
                        vcrep.type = "Dcard"
                        vcrep.brand_id = brand_id
                        vcrep.product_id = prdct_id
                        vcrep.quantity = quantity
                        vcrep.amount = amt
                        vcrep.rtype = "Web"
                        vcrep.denominations = deno
                        ms = mllist[::-1]
                        mu = sponserlist[::-1]
                        ad=UserData.objects.get(username=admin)
                        if(mllen==1):
                            vcrep.margin1=ms[0]
                            vcrep.sponser1=ad
                            vcrep.sponser2=UserData.objects.get(username=sponserlist[0])
                        elif(mllen==2):
                            vcrep.margin1=ms[0]
                            vcrep.margin2=ms[1]
                            vcrep.sponser1=ad
                            vcrep.sponser2=UserData.objects.get(username=sponserlist[1])
                            vcrep.sponser3=UserData.objects.get(username=sponserlist[0])
                        else:
                            vcrep.margin1=ms[0]
                            vcrep.margin2=ms[1]
                            vcrep.margin3=ms[2]
                            vcrep.sponser1=ad
                            vcrep.sponser2=UserData.objects.get(username=sponserlist[2])
                            vcrep.sponser3=UserData.objects.get(username=sponserlist[1])
                            vcrep.sponser4=UserData.objects.get(username=sponserlist[0])
                        vcrep.save()
                        obj = vcloudtransactions.objects.latest('id')
                        print(obj.id)
                        content["data"] = result
                        content["res_status"]="success"
                        content["trid"]=obj.id
                    except:
                        content["res_status"]="Failed"
                else:
                    for i in prdctdet:
                        i.suser=None
                        i.save()
                    content["res_status"]="Failed"
            return JsonResponse(content,safe=False)
        else:
            return redirect(resellerdcardstore)
    else:
        return redirect(LoginPage)

def resellerdcardviewbrands(request):
    if request.session.has_key("user"):
        if request.session.has_key("user"):
            username = request.session["user"]
            vcdprod=dcardBrands.objects.all()
            resultlist=list()
            statuslist=list()
            for i in vcdprod:
                vca=datacardAssignments.objects.filter(assignedto=username,brand__brand=i.brand)
                if not vca:
                    statuslist.append(False)
                else:
                    statuslist.append(True)
            vcd=list(vcdprod)
            print(vcd)
            print(statuslist)
            #print(data)
            ldb=zip(vcd,statuslist)
            userdetails = UserData.objects.get(username=request.session["user"])
            return render(request,"reseller/dcard/viewBrands.html",{'pdcts':list(ldb),'user':userdetails})
        else:
            return redirect(LoginPage)



#________________RCARD_______________

def resellerRcardDashboard(request):
    if request.session.has_key("user"):
        last_month = datetime.today() - timedelta(days=1)
        username = request.session["user"]
        #print(last_month)
        reseller = UserData.objects.filter(sponserId=username,postId="Sub_Reseller")
        #print(reseller)
        resellerlist=list()
        for i in reseller:
            resellerdata={'username':i.username,'name':i.name}
            resellerlist.append(resellerdata)
        username = request.session["user"]
        type = request.session["usertype"]
        try:
            user = UserData.objects.get(username = username, postId = type)
        except UserData.DoesNotExist:
            return redirect(LoginPage)
        userdetails = UserData.objects.get(username=request.session["user"])
        username=request.session["user"]
        last_month = datetime.today() - timedelta(days=1)
        vcloudtxns = vcloudtransactions.objects.filter(date__gte=last_month,sponser2__username=username,type="Rcard").order_by('-date')
        content=list()
        topuser=list()
        noofrecords=0
        productsum =0
        quantitysum =0
        profitsum =0
        count=0
        for i in vcloudtxns:
            count=count+1
            cost=i.denominations+i.margin1
            productsum=productsum+(cost*i.quantity)
            quantitysum=quantitysum+i.quantity
            if(i.saleduser.username==username):
                profit=0
                #data3={'user':i.sponser2.name,'amount':(i.denominations*i.quantity)}
                data={"id":i.id,"saleduser":i.sponser2.name,"role":i.sponser2.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                content.append(data)
                profitsum = profitsum+profit
            else:
                profit=i.margin2*i.quantity
                data3={'user':i.sponser3.name,'amount':(cost*i.quantity)}
                topuser.append(data3)
                data={"id":i.id,"saleduser":i.sponser3.name,"role":i.sponser3.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                content.append(data)
                profitsum = profitsum+profit
        box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum,'noofrecords':count}
        brand = rcardAssignments.objects.filter(assignedto=username).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description','margin')
        product=list()
        print(brand)
        for i in brand:
            print(i['brand__id'])
            pd=rcardProducts.objects.filter(brand=i['brand__id'],status=True).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
            lpd=list(pd)
            count=0
            if not lpd:
                pass
                #print("Haiii")
            else:
                username=request.session["user"]
                productcost=Decimal(lpd[0]['brand__denomination'])
                print(productcost)
                while(True):
                    userdet2=UserData.objects.filter(username=username).values('sponserId','postId')
                    print(userdet2)
                    margindet=rcardAssignments.objects.filter(assignedto=username,brand__brand=i['brand__brand']).values('margin')
                    if(userdet2[0]['postId']=="Admin"):
                        break;
                    else:
                        print(margindet[0]['margin'])
                        productcost = Decimal(productcost)+Decimal(margindet[0]['margin'])
                        print(productcost)
                        username=userdet2[0]['sponserId']
                    count=int(count)+1
                data={"brand":lpd[0]['brand__brand'],'rate':productcost}
                product.append(data)
                #print(content)
        print(product)
        list3=list()
        sorted_users = sorted(topuser, key=itemgetter('user'))

        for key, group in itertools.groupby(sorted_users, key=lambda x:x['user']):
            amountsum=0
            for g in group:
                amountsum=amountsum+g["amount"]
                #print(amountsum)
            data5={'user':key,'amount':amountsum}
            list3.append(data5)


        return render(request,"reseller/rcard/dashboard-rcard.html",{'filterform':rcardDashboardfilter,'reseller':resellerlist,'recenttransactions':content,'products':product,'user':user,'topuser':list3,'last_month':last_month,'boxval':box_data})
    else:
        return redirect(LoginPage)

def filterresellerrcardhomepage(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = rcardDashboardfilter(request.POST or None)
            print(form.errors)
            if form.is_valid():
                currentuser=request.session["user"]
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                usertype=form.cleaned_data.get("usertype")
                uuusername=form.cleaned_data.get("username")
                #mffromdate=datetime.strptime(fromdate, '%b %d %Y %I:%M%p')
                #print(type(fromdate))g
                print(fromdate.strftime("%B %d, %Y"))
                last_month=fromdate.strftime("%B %d, %I:%M %p")+" To "+todate.strftime("%B %d, %I:%M %p")
                reseller = UserData.objects.filter(sponserId=currentuser,postId="Sub_Reseller")
                #print(reseller)
                resellerlist=list()
                for i in reseller:
                    resellerdata={'username':i.username,'name':i.name}
                    resellerlist.append(resellerdata)
                #print(username)
                userdetails = UserData.objects.get(username=request.session["user"])
                vcloudtxns = vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate,sponser2__username=currentuser,type="Rcard",sponser3__username=uuusername).order_by('-date')
                content=list()
                topuser=list()
                noofrecords=0
                productsum =0
                quantitysum =0
                profitsum =0
                count=0
                for i in vcloudtxns:
                    count=count+1
                    cost=i.denominations+i.margin1
                    productsum=productsum+(cost*i.quantity)
                    quantitysum=quantitysum+i.quantity
                    if(i.saleduser.username==username):
                        profit=0
                        #data3={'user':i.sponser2.name,'amount':(i.denominations*i.quantity)}
                        data={"id":i.id,"saleduser":i.sponser2.name,"role":i.sponser2.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                        content.append(data)
                        profitsum = profitsum+profit
                    else:
                        profit=i.margin2*i.quantity
                        data3={'user':i.sponser3.name,'amount':(cost*i.quantity)}
                        topuser.append(data3)
                        data={"id":i.id,"saleduser":i.sponser3.name,"role":i.sponser3.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                        content.append(data)
                        profitsum = profitsum+profit
                box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum,'noofrecords':count}
                brand = rcardAssignments.objects.filter(assignedto=currentuser).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description','margin')
                product=list()
                print(brand)
                for i in brand:
                    print(i['brand__id'])
                    pd=rcardProducts.objects.filter(brand=i['brand__id'],status=True).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
                    lpd=list(pd)
                    count=0
                    if not lpd:
                        pass
                        #print("Haiii")
                    else:
                        username=request.session["user"]
                        productcost=Decimal(lpd[0]['brand__denomination'])
                        print(productcost)
                        while(True):
                            userdet2=UserData.objects.filter(username=username).values('sponserId','postId')
                            print(userdet2)
                            margindet=rcardAssignments.objects.filter(assignedto=username,brand__brand=i['brand__brand']).values('margin')
                            if(userdet2[0]['postId']=="Admin"):
                                break;
                            else:
                                print(margindet[0]['margin'])
                                productcost = Decimal(productcost)+Decimal(margindet[0]['margin'])
                                print(productcost)
                                username=userdet2[0]['sponserId']
                            count=int(count)+1
                        data={"brand":lpd[0]['brand__brand'],'rate':productcost}
                        product.append(data)
                        #print(content)
                print(product)
                list3=list()
                sorted_users = sorted(topuser, key=itemgetter('user'))

                for key, group in itertools.groupby(sorted_users, key=lambda x:x['user']):
                    amountsum=0
                    for g in group:
                        amountsum=amountsum+g["amount"]
                        #print(amountsum)
                    data5={'user':key,'amount':amountsum}
                    list3.append(data5)
                return render(request,"reseller/rcard/dashboard-rcard.html",{'filterform':rcardDashboardfilter,'reseller':resellerlist,'recenttransactions':content,'products':product,'user':userdetails,'topuser':list3,'last_month':last_month,'boxval':box_data})
            else:
                return redirect(resellerRcardDashboard)
        else:
            return(resellerRcardDashboard)
    else:
        return redirect(LoginPage)

def resellerprofilercard(request):
    if request.session.has_key("user"):
        user = request.session["user"]
        userDet = UserData.objects.get(username=user)
        return render(request,"reseller/rcard/editProfile.html",{'user':userDet})
    else:
        return redirect(LoginPage)

def reselleraddResellerRcard(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"reseller/rcard/addReseller.html",{'form':AddUserDataForm,'user':userdetails})
    else:
        return redirect(LoginPage)

def reselleraddUserRcard(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"reseller/rcard/addUser.html",{'form':AddUserDataForm,'user':userdetails})
    else:
        return redirect(LoginPage)

def resellerviewResellerRcard(request):
    if request.session.has_key("user"):
        resellers = UserData.objects.filter(sponserId=request.session["user"],postId="Sub_Reseller")
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"reseller/rcard/viewResellers.html",{'resellers':resellers,'user':userdetails})
    else:
        return redirect(LoginPage)

def resellerviewUserRcard(request):
    if request.session.has_key("user"):
        user = request.session["user"]
        resellers = UserData.objects.filter(postId="User",sponserId=user)
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"reseller/rcard/viewUser.html",{'resellers':resellers,'user':userdetails})
    else:
        return redirect(LoginPage)

def resellerbalanceTransferRcard(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        bthist=balanceTransactionReport.objects.filter(source=userdetails,category="BT").order_by('-date')
        #print(bthist)
        return render(request,"reseller/rcard/balanceTransfer.html",{'bthist':bthist,'user':userdetails})
    else:
        return redirect(LoginPage)

def reselleraddPaymentRcard(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        phist=fundTransactionReport.objects.filter(source=userdetails).order_by('-date')
        return render(request,"reseller/rcard/addPayment.html",{'phist':phist})
    else:
        return redirect(LoginPage)

def resellerrcardreport(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        username=request.session["user"]
        last_month = datetime.today() - timedelta(days=1)
        vcloudtxns = vcloudtransactions.objects.filter(date__gte=last_month,sponser2__username=username).order_by('-date')
        #vcloudtxns = vcloudtransactions.objects.all().order_by('-date')
        reseller=UserData.objects.filter(sponserId=username,postId="Reseller")
        resellerlist=list()
        vcbrand=vcloudBrands.objects.all()
        vcbrandlist=list()
        for b in vcbrand:
            branddata={'brand':b.brand}
            vcbrandlist.append(branddata)

        for i in reseller:
            resellerdata={'username':i.username,'name':i.name}
            resellerlist.append(resellerdata)
        content=list()
        noofrecords=0
        productsum =0
        quantitysum =0
        profitsum =0
        cost=0
        for i in vcloudtxns:
            cost=i.denominations+i.margin1
            productsum=productsum+(cost*i.quantity)
            quantitysum=quantitysum+i.quantity
            if(i.saleduser.username==username):
                profit=0
                data={"id":i.id,"saleduser":i.sponser2.name,"role":i.sponser2.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                content.append(data)
                profitsum = profitsum+profit
            else:
                profit=(i.margin2*i.quantity)
                data={"id":i.id,"saleduser":i.sponser3.name,"role":i.sponser3.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                content.append(data)
                profitsum = profitsum+profit
        box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum}
        return render(request,"reseller/rcard/rcardreport.html",{'filterform':vcloudreportfilterform,'products':content,'user':userdetails,'reseller':resellerlist, 'brand':vcbrandlist,'box':box_data,'date':last_month})
    else:
        return redirect(LoginPage)

def filterresellerrcard_report(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            form = vcloudreportfilterform(request.POST or None)
            print(form.errors)
            if form.is_valid():
                username=request.session["user"]
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                usertype=form.cleaned_data.get("usertype")
                fusername=form.cleaned_data.get("username")
                type=form.cleaned_data.get("type")
                brand=form.cleaned_data.get("brand")
                #print(brand,fusername)
                fuser=''
                if(fusername!='All'):
                    filterdata=UserData.objects.get(username=fusername)
                    fuser=filterdata.name
                else:
                    fuser=fusername
                filter={'ffdate':fromdate,'ttdate':todate,'fuser':fuser}
                userdetails = UserData.objects.get(username=request.session["user"])
                reseller=UserData.objects.filter(sponserId=username,postId="Sub_Reseller")
                resellerlist=list()
                vcbrand=vcloudBrands.objects.all()
                vcbrandlist=list()
                for b in vcbrand:
                    branddata={'brand':b.brand}
                    vcbrandlist.append(branddata)

                for i in reseller:
                    resellerdata={'username':i.username,'name':i.name}
                    resellerlist.append(resellerdata)

                content=list()
                noofrecords = 0
                productsum = 0
                quantitysum = 0
                profitsum = 0
                vcloudtxns=vcloudtransactions()
                try:
                    print(usertype)
                    print(fusername)
                    print(type)
                    print(brand)
                    if(usertype=="All" and fusername=="All" and type=="All" and brand=="All"):
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser2__username=username).order_by('-date')
                        print("One")
                    elif(usertype=="All" and fusername=="All" and type=="All" and brand !="All"):
                        print("TWo")
                        vcloudtxns==vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser2__username=username, brand=brand).order_by('-date')
                    elif(usertype=="All" and fusername=="All" and type !="All" and brand =="All"):
                        print("Three")
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser2__username=username, type=type).order_by('-date')
                    elif(usertype=="All" and fusername=="All" and type !="All" and brand !="All"):
                        print("four")
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser2__username=username, brand=brand).order_by('-date')
                    elif(usertype=="All" and fusername!="All" and type !="All" and brand !="All"):
                        print('five')
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, type=type, sponser2__username=username, sponser3__username=fusername, brand=brand).order_by('-date')
                    elif(usertype !="All" and fusername =="All" and type =="All" and brand !="All"):
                        print('Six')
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser3__postId=usertype, sponser2__username=username).order_by('-date')
                    elif(usertype !="All" and fusername =="All" and type =="All" and brand =="All"):
                        print('Six')
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser2__username=username, sponser3__postId=usertype).order_by('-date')
                    elif(usertype =="All" and fusername !="All" and type =="All" and brand =="All"):
                        print('Six')
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser2__username=username, sponser3__username=fusername).order_by('-date')
                    elif(usertype !="All" and fusername !="All" and type =="All" and brand =="All"):
                        print('Six')
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser2__username=username, sponser3__username=fusername).order_by('-date')
                    else:
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser2__username=username, sponser3__username=fusername,brand=brand).order_by('-date')
                    print(vcloudtxns)
                    for i in vcloudtxns:
                        cost=i.denominations+i.margin1
                        productsum=productsum+(cost*i.quantity)
                        quantitysum=quantitysum+i.quantity
                        if(i.saleduser.username==username):
                            profit=0
                            data={"id":i.id,"saleduser":i.sponser2.name,"role":i.sponser2.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                            content.append(data)
                            profitsum = profitsum+profit
                        else:
                            profit=(i.margin2*i.quantity)
                            data={"id":i.id,"saleduser":i.sponser3.name,"role":i.sponser3.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                            content.append(data)
                            profitsum = profitsum+profit
                except:
                    pass
                box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum}
                return render(request,"reseller/rcard/rcardreport.html",{'filterform':vcloudreportfilterform,'products':content,'user':userdetails,'reseller':resellerlist, 'brand':vcbrandlist,'box':box_data,'filter':filter})
            else:
                return redirect(resellerrcardreport)
        else:
            return redirect(resellerrcardreport)
    else:
        return redirect(LoginPage)

def resellerbTReportRcard(request):
    if request.session.has_key("user"):
        username = request.session["user"]
        userdetails = UserData.objects.get(username=request.session["user"])
        reseller = UserData.objects.filter(sponserId=username,postId="Sub_Reseller")
        fromsum = balanceTransactionReport.objects.filter(source=userdetails,category='BT').aggregate(Sum('amount'))
        tosum = balanceTransactionReport.objects.filter(destination=userdetails,category='BT').aggregate(Sum('amount'))
        bthist = balanceTransactionReport.objects.filter(source=userdetails).order_by('-date') | balanceTransactionReport.objects.filter(destination=userdetails).order_by('-date')
        return render(request,"reseller/rcard/balanceTransferReport.html",{'form':balancetransferfilterform,'reseller':reseller,'bthist':bthist,'fromsum':fromsum['amount__sum'],'tosum':tosum['amount__sum'],'user':userdetails})
    else:
        return redirect(LoginPage)

def filterresellerrcardbtreport(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            form = balancetransferfilterform(request.POST or None)
            print(form.errors)
            if form.is_valid():
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                usertype=form.cleaned_data.get("usertype")
                susername=form.cleaned_data.get("username")
                username = request.session["user"]
                filter={'ffdate':fromdate,'ttdate':todate,'fuser':susername}
                userdetails = UserData.objects.get(username=request.session["user"])
                reseller = UserData.objects.filter(sponserId=username,postId="Sub_Reseller")
                fromsum=None
                tosum=None
                bthist=None
                try:
                    if(usertype == "Self"):
                        fromsum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails).aggregate(Sum('amount'))
                        tosum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdetails).aggregate(Sum('amount'))
                        bthist = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdetails)
                    elif(usertype == "All" and susername == "All"):
                        fromsum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails).aggregate(Sum('amount'))
                        tosum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdetails).aggregate(Sum('amount'))
                        bthist = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails)
                    elif(usertype!="All" and susername == "All"):
                        fromsum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__postId=usertype).aggregate(Sum('amount'))
                        tosum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdetails).aggregate(Sum('amount'))
                        bthist = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__postId=usertype)
                    else:
                        fromsum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__username=susername).aggregate(Sum('amount'))
                        tosum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdetails).aggregate(Sum('amount'))
                        bthist = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__username=susername)
                except:
                    pass
                return render(request,"reseller/dcard/balanceTransferReport.html",{'form':balancetransferfilterform,'reseller':reseller,'bthist':bthist,'fromsum':fromsum['amount__sum'],'tosum':tosum['amount__sum'],'user':userdetails,'filter':filter})
            else:
                return redirect(resellerbTReportRcard)
        else:
            return redirect(resellerbTReportRcard)
    else:
        return redirect(LoginPage)

def resellerpaymentReportRcard(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        reseller = UserData.objects.filter(sponserId=request.session["user"],postId="Sub_Reseller")
        phist = fundTransactionReport.objects.filter(source=userdetails).order_by('-date')|fundTransactionReport.objects.filter(destination=userdetails).order_by('-date')
        bsum = fundTransactionReport.objects.filter(source=userdetails).aggregate(Sum('amount'))
        return render(request,"reseller/rcard/paymentReport.html",{'form':paymentfilterform,'reseller':reseller,'phist':phist,'sum':bsum['amount__sum'],'user':userdetails})
    else:
        return redirect(LoginPage)

def filterresellerrcardpaymentreport(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            form = balancetransferfilterform(request.POST or None)
            print(form.errors)
            if form.is_valid():
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                usertype=form.cleaned_data.get("usertype")
                susername=form.cleaned_data.get("username")
                username = request.session["user"]
                filter={'ffdate':fromdate,'ttdate':todate,'fuser':susername}
                userdetails = UserData.objects.get(username=request.session["user"])
                reseller = UserData.objects.filter(sponserId=username,postId="Sub_Reseller")
                bsum=None
                phist=None
                try:
                    if(usertype == "Self" ):
                        bsum = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdetails).aggregate(Sum('amount'))
                        phist = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdetails)
                    elif(usertype == "All" and susername == "All"):
                        bsum = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails).aggregate(Sum('amount'))
                        phist = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails)
                        #print(phist)
                        #print("phist")
                    elif(usertype!="All" and susername == "All"):
                        #print(usertype)
                        bsum = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails).aggregate(Sum('amount'))
                        phist = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails, destination__postId=usertype)
                        #print("Haiii")
                    else:
                        bsum = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__username=susername).aggregate(Sum('amount'))
                        phist = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__username=susername)
                except Exception as e:
                    print(e)
                    pass
                return render(request,"reseller/rcard/paymentReport.html",{'form':paymentfilterform,'reseller':reseller,'phist':phist,'sum':bsum['amount__sum'],'user':userdetails,'filter':filter})
            else:
                return redirect(resellerpaymentReportRcard)
        else:
            return redirect(resellerpaymentReportRcard)
    else:
        return redirect(LoginPage)

def getReachargeProductCost(username,brand):
    prdcts=rcardBrands.objects.get(brand=brand)
    prdctcost=0
    prdctcost = Decimal(prdcts.denomination)
    margins=0
    print("helloo")
    while(True):
        userdet = UserData.objects.filter(username=username).values('sponserId','postId')
        pdct = rcardAssignments.objects.filter(assignedto=username, brand__brand=brand).values('margin')
        if(pdct):
            if(userdet[0]['postId']=="Admin"):
                break;
            else:
                prdctcost = prdctcost+Decimal(pdct[0]['margin'])
            username=userdet[0]['sponserId']
        else:
            break;
    #print(prdctcost)
    return prdctcost


def resellerassignRCardBrands(request):
    if request.session.has_key("user"):
        brands = rcardAssignments.objects.filter(assignedto=request.session["user"]).values('brand','brand__brand','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
        username=request.session["user"]
        bd=list(brands)
        prdcts=list()
        costs=list()
        for i in brands:
            prd=rcardBrands.objects.get(brand=i['brand__brand'])
            #prd=rcardProducts.objects.filter(brand__brand=i['brand__brand'], status=True).order_by('brand').values('brand').annotate(productcount=Count('brand')).values('brand','brand__brand','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
            if(prd):
                cost=getReachargeProductCost(username,i["brand__brand"])
                data={'brand__brand':prd.brand,'brand__logo':prd.logo.url,'brand__id':prd.id,'cost':cost,'brand__currency':prd.currency,'brand__description':prd.description}
                prdcts.append(data)
            else:
                pass

        #print(pddata[0])
        resellers = UserData.objects.filter(postId="Sub_Reseller",sponserId=request.session["user"])
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"reseller/rcard/assignRcardbrand.html",{'brands':bd,'products':prdcts,'resellers':resellers,'user':userdetails})
    else:
        return redirect(LoginPage)

def resellerrcardstore(request):
    if request.session.has_key("user"):
        username=request.session["user"]
        user = UserData.objects.get(username=username)
        ads = adverisements.objects.filter(adtype="Image",usertype="Reseller",ctype="Rcard").order_by('-id')[:10]
        btnlist=list()
        content=list()
        dproducts = rcardAssignments.objects.filter(assignedto=username).order_by('brand').values('brand__brand','margin')
        for i in dproducts:
            buttons=(i["brand__brand"]).split(" ")
            if buttons[0] not in btnlist:
                btnlist.append(buttons[0])
        if(len(btnlist)!=0):
            dcardproducts = rcardAssignments.objects.filter(assignedto=username,brand__brand__contains=btnlist[0]).order_by('brand').values('brand__brand','margin')
            for i in dcardproducts:
                dcp=rcardProducts.objects.filter(brand__brand=i["brand__brand"],status=True).order_by('brand').values('brand').annotate(count=Count('brand')).values('count','brand__id','brand__brand','brand__description','brand__denomination','brand__logo','count','brand__currency')
                if(len(dcp)>0):
                    cost=getRcardProductCost(username,dcp[0]["brand__brand"])
                    data={'brand__id':dcp[0]['brand__id'],'brand__brand':dcp[0]['brand__brand'],'brand__logo':dcp[0]['brand__logo'],'brand__description':dcp[0]['brand__description'],'brand__currency':dcp[0]['brand__currency'],'count':dcp[0]['count'],'cost':cost}
                    content.append(data)
                else:
                    pass
        else:
            pass
        print(content)
        return render(request,"reseller/rcard/rcardstore.html",{'dcardproducts':content,'btnlist':btnlist,'user':user,'ads':ads})
    else:
        return redirect(LoginPage)

def getVcloudCost(id,username):
    prdctcost=0
    prdcts=vcloudtransactions.objects.get(id=id)
    prdctcost = Decimal(prdcts.denominations)
    margins=0
    if(prdcts.type == "Vcloud"):
        while(True):
            try:
                userdet = UserData.objects.filter(username=username).values('sponserId','postId')
                pdct = vcloudAssignments.objects.filter(assignedto=username, brand__brand=prdcts.brand).values('margin')
                if(userdet[0]['postId']=="Admin"):
                    break;
                else:
                    prdctcost = prdctcost+Decimal(pdct[0]['margin'])
                username=userdet[0]['sponserId']
            except:
                pass
    elif(prdcts.type == "Dcard"):
        while(True):
            try:
                userdet = UserData.objects.filter(username=username).values('sponserId','postId')
                pdct = datacardAssignments.objects.filter(assignedto=username, brand__brand=prdcts.brand).values('margin')
                if(userdet[0]['postId']=="Admin"):
                    break;
                else:
                    prdctcost = prdctcost+Decimal(pdct[0]['margin'])
                username=userdet[0]['sponserId']
            except:
                pass
    else:
        while(True):
            try:
                userdet = UserData.objects.filter(username=username).values('sponserId','postId')
                pdct = rcardAssignments.objects.filter(assignedto=username, brand__id=prdcts.brand_id).values('margin')
                if(userdet[0]['postId']=="Admin"):
                    break;
                else:
                    prdctcost = prdctcost+Decimal(pdct[0]['margin'])
                username=userdet[0]['sponserId']
            except:
                pass
    return prdctcost


def viewfilteredreachargestore(brand):
    brands=rcardProducts.objects.filter(brand__brand__contains=brand,status=True).order_by('brand').values('brand').annotate(productcount=Count('brand')).values('productcount','brand__brand','brand__id','brand__description','brand__denomination','brand__logo','brand__currency')
    return brands

def resellerfilterrcardstore(request,brand):
    if request.session.has_key("user"):
        #print(brand)
        username=request.session["user"]
        user = UserData.objects.get(username=username)
        ads = adverisements.objects.filter(adtype="Image",usertype="Reseller",ctype="Rcard").order_by('-id')[:10]
        btnlist=list()
        dproducts = rcardAssignments.objects.filter(assignedto=username).order_by('brand').values('brand__brand','margin')
        for i in dproducts:
            buttons=(i["brand__brand"]).split(" ")
            if buttons[0] not in btnlist:
                btnlist.append(buttons[0])
        dcardproducts = rcardAssignments.objects.filter(assignedto=username,brand__brand__contains=brand).order_by('brand').values('brand__brand','margin')
        content=list()
        #print(buttons)
        for i in dcardproducts:
            dcp=rcardProducts.objects.filter(brand__brand=i["brand__brand"],status=True).order_by('brand').values('brand').annotate(count=Count('brand')).values('count','brand__id','brand__brand','brand__description','brand__denomination','brand__logo','count','brand__currency')
            if(len(dcp)>0):
                buttons=(dcp[0]["brand__brand"]).split(" ")
                if buttons[0] not in btnlist:
                    btnlist.append(buttons[0])
                cost=getRcardProductCost(username,dcp[0]["brand__brand"])
                data={'brand__id':dcp[0]['brand__id'],'brand__brand':dcp[0]['brand__brand'],'brand__logo':dcp[0]['brand__logo'],'brand__description':dcp[0]['brand__description'],'brand__currency':dcp[0]['brand__currency'],'count':dcp[0]['count'],'cost':cost}
                content.append(data)
            else:
                pass;
            print(content)
        return render(request,"reseller/rcard/rcardstore.html",{'dcardproducts':content,'btnlist':btnlist,'user':user,'ads':ads})
    else:
        return redirect(LoginPage)


def editresellerProfileRcard(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            user = request.session["user"]
            name = request.POST.get('name', None)
            address = request.POST.get('address', None)
            email = request.POST.get('email', None)
            mobileno = request.POST.get('mobileno', None)
            userDet = UserData.objects.get(username=user)
            userDet.name = name
            userDet.address = address
            userDet.email = email
            userDet.mobileno = mobileno
            userDet.save()
            messages.success(request, 'Successfully Updated')
            return redirect(resellerprofilercard)
        else:
            messages.warning(request,'Internal Error Occured')
            return redirect(resellerprofilercard)
    else:
        return redirect(LoginPage)

def resellerrcardsubmitReseller(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = AddUserDataForm(request.POST or None)
            print(form.errors)
            if form.is_valid():
                username=form.cleaned_data.get("username")
                password=form.cleaned_data.get("password")
                print(username)
                hashkey = username+password
                hash = hashlib.sha256(hashkey.encode()).hexdigest()
                sponser = request.session["user"]
                sponseruser=UserData.objects.get(username=sponser)
                Userdata=form.save(commit=False)
                Userdata.postId="Sub_Reseller"
                Userdata.sponserId = sponseruser
                Userdata.status = True
                Userdata.balance = 0
                Userdata.targetAmt = 0
                Userdata.rentalAmt = 0
                Userdata.dcard_status = True
                Userdata.rcard_status = True
                Userdata.password = hash
                Userdata.save()
                messages.success(request,'Successfully Added')
                return redirect(reselleraddResellerRcard)
            else:
                userdetails = UserData.objects.get(username=request.session["user"])
                messages.warning(request, form.errors)
                form = AddUserDataForm()
                return render(request,"reseller/rcard/addReseller.html",{'form':AddUserDataForm,'user':userdetails})
        else:
            userdetails = UserData.objects.get(username=request.session["user"])
            form = AddUserDataForm()
            return render(request,"reseller/rcard/addReseller.html",{'form':AddUserDataForm,'user':userdetails})
    else:
        return redirect(LoginPage)

def resellerrcardsubmitUser(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = AddUserDataForm(request.POST or None)
            print(form.errors)
            if form.is_valid():
                username=form.cleaned_data.get("username")
                password=form.cleaned_data.get("password")
                hashkey = username+password
                hash = hashlib.sha256(hashkey.encode()).hexdigest()
                sponser = request.session["user"]
                sponseruser=UserData.objects.get(username=sponser)
                Userdata=form.save(commit=False)
                Userdata.postId="User"
                Userdata.sponserId = sponseruser
                Userdata.status = True
                Userdata.balance = 0
                Userdata.targetAmt = 0
                Userdata.rentalAmt = 0
                Userdata.dcard_status = True
                Userdata.rcard_status = True
                Userdata.password = hash
                Userdata.save()
                messages.success(request, 'Successfully Added')
                return redirect(reselleraddUserRcard)
            else:
                userdetails = UserData.objects.get(username=request.session["user"])
                messages.warning(request, form.errors)
                form = AddUserDataForm()
                return render(request,"reseller/rcard/addUser.html",{'form':AddUserDataForm,'user':userdetails})
        else:
            userdetails = UserData.objects.get(username=request.session["user"])
            form = AddUserDataForm()
            return render(request,"reseller/rcard/addUser.html",{'form':AddUserDataForm,'user':username})
    else:
        return redirect(LoginPage)

def resellersubBalTransRcard(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            userType = request.POST.get('userType', None)
            user = request.POST.get('users', None)
            amount = request.POST.get('amount', None)
            userdet = UserData.objects.get(username=user)
            bal = userdet.balance
            newbal=bal+Decimal(amount)
            cdbal = userdet.targetAmt
            newcdbal = cdbal-Decimal(amount)
            userdet.targetAmt = newcdbal
            userdet.balance = newbal
            userdet.save()
            userdetails = UserData.objects.get(username=request.session["user"])
            btreport = balanceTransactionReport()
            btreport.source = userdetails
            btreport.destination = userdet
            btreport.category = "BT"
            btreport.pbalance = bal
            btreport.nbalance = newbal
            btreport.cramount = newcdbal
            btreport.amount = amount
            btreport.remarks = 'Added To Balance'
            btreport.save()
            messages.success(request, 'Successfully Updated The balance')
            return redirect(resellerbalanceTransferRcard)
            #userdata=UserData.objects.get(username=)
        else:
            messages.warning(request, 'Internal Error Occured')
            return redirect(resellerbalanceTransferRcard)
    else:
        return redirect(LoginPage)

def resellerrcardsubPayTrans(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            userType = request.POST.get('userType', None)
            user = request.POST.get('users', None)
            amount = request.POST.get('amount', None)
            remarks = request.POST.get('remarks', None)
            userdet = UserData.objects.get(username=user)
            obalance = userdet.targetAmt
            cdbal = userdet.targetAmt
            newcdbal = cdbal+Decimal(amount)
            userdet.targetAmt = newcdbal
            userdet.save()
            closeuser = UserData.objects.get(username=user)
            userdetails = UserData.objects.get(username=request.session["user"])
            ftreport=fundTransactionReport()
            ftreport.source = userdetails
            ftreport.destination = userdet
            ftreport.obalance = obalance
            ftreport.cbalance = closeuser.targetAmt
            ftreport.role = userType
            ftreport.amount = amount
            ftreport.balance = newcdbal
            ftreport.remarks = remarks
            ftreport.save()
            messages.success(request, 'Successfully Updated The balance')
            return redirect(reselleraddPaymentRcard)
        else:
            messages.warning(request, 'Internal Error Occured')
            return redirect(reselleraddPaymentRcard)
    else:
        return redirect(LoginPage)

def buy_rcard_brands(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            username=request.session["user"]
            brand = request.POST.get('brandid', None)
            quantity = request.POST.get('quantity', None)
            amt = request.POST.get('amt', None)
            branddet=rcardBrands.objects.get(brand=brand)
            userdet=UserData.objects.get(username=request.session["user"])
            ctime=datetime.now()
            time = timedelta(minutes = 5)
            now_minus_5 = ctime - time
            checkqty=rcardProducts.objects.filter(Q(brand__brand=brand) & Q(status=True) & (Q(sdate__isnull=True) | Q(sdate__lte=now_minus_5))).values('brand').annotate(productcount=Count('brand')).values('productcount')
            print(checkqty)
            needamt=0;
            result=list()
            content=dict()
            licheckqty=list(checkqty)
            brand_id=0
            deno=0
            if(licheckqty[0]['productcount'] >= int(quantity)):
                usertype=''
                marginlist=list()
                margins=0
                count=0;
                flag=True
                prdct_id=''
                mllist=list()
                sponserlist=list()
                prdctdet = rcardProducts.objects.filter(Q(brand__brand=brand) & Q(status=True) & (Q(sdate__isnull=True) | Q(sdate__lte=now_minus_5)))[:int(quantity)]
                ctime = datetime.now()
                for i in prdctdet:
                    i.productstatus=1
                    i.suser = userdet
                    i.sdate = ctime
                    i.save()
                count=0
                admin=''
                while(True):
                    userdet2=UserData.objects.filter(username=username).values('sponserId','postId','balance')
                    margindet=rcardAssignments.objects.filter(assignedto=username,brand__brand=brand).values('margin')
                    if(userdet2[0]['postId']=="Admin"):
                        admin=username
                        break;
                    else:
                        cost=Decimal(amt)
                        prdctcost = (cost*Decimal(quantity))-(Decimal(margins)*Decimal(quantity))
                        margins=margins+Decimal(margindet[0]['margin'])
                        #print(prdctcost)
                        #print(cost)
                        if(userdet2[0]['balance']>=prdctcost):
                            data={'margin':margindet[0]['margin'],'balance':userdet2[0]['balance'],'username':username,'prdctcost':prdctcost}
                            marginlist.append(data)
                            mllist.append(margindet[0]['margin'])
                            sponserlist.append(username)
                        else:
                            flag=False
                            print(flag)
                            break;
                    username=userdet2[0]['sponserId']
                if(flag):
                    try:
                        prdctcddet=rcardProducts.objects.filter(brand__brand=brand,status=True,productstatus=1,suser=userdet,sdate=ctime)[:int(quantity)]
                        for h in prdctcddet:
                            h.status=False
                            h.save()
                            brand_id=h.brand.id
                            deno=h.brand.denomination
                            prdct_id=prdct_id+""+str(h.id)+","
                            res={"productid":h.id,"carduname":h.username,'brand':h.brand.brand,'brand_logo':h.brand.logo.url, 'status':h.status,'suser':username,'sdate':h.sdate}
                            result.append(res)
                        ml=marginlist[::-1]
                        for k in ml:
                            uname = k['username']
                            margin = k['margin']
                            balance = k['balance']
                            pcost = k['prdctcost']
                            cb=Decimal(balance)-Decimal(pcost)
                            userd=UserData.objects.get(username=uname)
                            userd.balance=cb
                            userd.save()
                        mllen = len(mllist)
                        vcrep=vcloudtransactions()
                        vcrep.saleduser = userdet
                        vcrep.brand = brand
                        vcrep.type = "Rcard"
                        vcrep.brand_id = brand_id
                        vcrep.product_id = prdct_id
                        vcrep.quantity = quantity
                        vcrep.amount = amt
                        vcrep.rtype = "Web"
                        vcrep.denominations = deno
                        ms = mllist[::-1]
                        mu = sponserlist[::-1]
                        ad=UserData.objects.get(username=admin)
                        if(mllen==1):
                            vcrep.margin1=ms[0]
                            vcrep.sponser1=ad
                            vcrep.sponser2=UserData.objects.get(username=sponserlist[0])
                        elif(mllen==2):
                            vcrep.margin1=ms[0]
                            vcrep.margin2=ms[1]
                            vcrep.sponser1=ad
                            vcrep.sponser2=UserData.objects.get(username=sponserlist[1])
                            vcrep.sponser3=UserData.objects.get(username=sponserlist[0])
                        else:
                            vcrep.margin1=ms[0]
                            vcrep.margin2=ms[1]
                            vcrep.margin3=ms[2]
                            vcrep.sponser1=ad
                            vcrep.sponser2=UserData.objects.get(username=sponserlist[2])
                            vcrep.sponser3=UserData.objects.get(username=sponserlist[1])
                            vcrep.sponser4=UserData.objects.get(username=sponserlist[0])
                        vcrep.save()
                        obj = vcloudtransactions.objects.latest('id')
                        print(obj.id)
                        content["data"] = result
                        content["res_status"]="success"
                        content["trid"]=obj.id
                    except:
                        content["res_status"]="Failed"
                else:
                    for i in prdctdet:
                        i.suser=None
                        i.save()
                    content["res_status"]="Failed"
            return JsonResponse(content,safe=False)
        else:
            return redirect(resellerrcardstore)
    else:
        return redirect(LoginPage)

def resellerrcardviewbrands(request):
    if request.session.has_key("user"):
        if request.session.has_key("user"):
            username = request.session["user"]
            vcdprod=rcardBrands.objects.all()
            resultlist=list()
            statuslist=list()
            for i in vcdprod:
                vca=rcardAssignments.objects.filter(assignedto=username,brand__brand=i.brand)
                if not vca:
                    statuslist.append(False)
                else:
                    statuslist.append(True)
            vcd=list(vcdprod)
            print(vcd)
            print(statuslist)
            #print(data)
            ldb=zip(vcd,statuslist)
            userdetails = UserData.objects.get(username=request.session["user"])
            return render(request,"reseller/rcard/viewBrands.html",{'pdcts':list(ldb),'user':userdetails})
        else:
            return redirect(LoginPage)

#________________________________________________________________Sub_Reseller_______________________________________________________________

#________________VCLOUD_______________

def subresellervcloudhomePage(request):
    if request.session.has_key("user"):
        last_month = datetime.today() - timedelta(days=1)
        username = request.session["user"]
        #print(last_month)
        reseller = UserData.objects.filter(sponserId=username,postId="User")
        #print(reseller)
        resellerlist=list()
        for i in reseller:
            resellerdata={'username':i.username,'name':i.name}
            resellerlist.append(resellerdata)
        username = request.session["user"]
        type = request.session["usertype"]
        try:
            user = UserData.objects.get(username = username, postId = type)
        except UserData.DoesNotExist:
            return redirect(LoginPage)
        userdetails = UserData.objects.get(username=request.session["user"])
        username=request.session["user"]
        last_month = datetime.today() - timedelta(days=1)
        vcloudtxns = vcloudtransactions.objects.filter(date__gte=last_month,sponser3__username=username,type="Vcloud").order_by('-date')
        content=list()
        topuser=list()
        noofrecords=0
        productsum =0
        quantitysum =0
        profitsum =0
        count=0
        for i in vcloudtxns:
            count=count+1
            cost=i.denominations+i.margin1+i.margin2
            productsum=productsum+(cost*i.quantity)
            quantitysum=quantitysum+i.quantity
            if(i.saleduser.username==username):
                profit=0
                #data3={'user':i.sponser2.name,'amount':(i.denominations*i.quantity)}
                data={"id":i.id,"saleduser":i.sponser3.name,"role":i.sponser3.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                content.append(data)
                profitsum = profitsum+profit
            else:
                profit=i.margin3*i.quantity
                data3={'user':i.sponser4.name,'amount':(cost*i.quantity)}
                topuser.append(data3)
                data={"id":i.id,"saleduser":i.sponser4.name,"role":i.sponser4.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                content.append(data)
                profitsum = profitsum+profit
        box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum,'noofrecords':count}
        brand = vcloudAssignments.objects.filter(assignedto=username).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description','margin')
        product=list()
        print(brand)
        for i in brand:
            print(i['brand__id'])
            pd=vcloudProducts.objects.filter(brand=i['brand__id'],status=True).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
            lpd=list(pd)
            count=0
            if not lpd:
                pass
                #print("Haiii")
            else:
                username=request.session["user"]
                productcost=Decimal(lpd[0]['brand__denomination'])
                print(productcost)
                while(True):
                    userdet2=UserData.objects.filter(username=username).values('sponserId','postId')
                    print(userdet2)
                    margindet=vcloudAssignments.objects.filter(assignedto=username,brand__brand=i['brand__brand']).values('margin')
                    if(userdet2[0]['postId']=="Admin"):
                        break;
                    else:
                        print(margindet[0]['margin'])
                        productcost = Decimal(productcost)+Decimal(margindet[0]['margin'])
                        print(productcost)
                        username=userdet2[0]['sponserId']
                    count=int(count)+1
                data={"brand":lpd[0]['brand__brand'],'rate':productcost}
                product.append(data)
                #print(content)
        print(product)
        list3=list()
        sorted_users = sorted(topuser, key=itemgetter('user'))

        for key, group in itertools.groupby(sorted_users, key=lambda x:x['user']):
            amountsum=0
            for g in group:
                amountsum=amountsum+g["amount"]
                #print(amountsum)
            data5={'user':key,'amount':amountsum}
            list3.append(data5)


        return render(request,"sub_reseller/vcloud/dashboard-vcloud.html",{'filterform':vcloudDashboardfilter,'reseller':resellerlist,'recenttransactions':content,'products':product,'user':user,'topuser':list3,'last_month':last_month,'boxval':box_data})
    else:
        return redirect(LoginPage)

def filtersubresellervcloudhomepage(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = vcloudDashboardfilter(request.POST or None)
            print(form.errors)
            if form.is_valid():
                currentuser=request.session["user"]
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                usertype=form.cleaned_data.get("usertype")
                uuusername=form.cleaned_data.get("username")
                #mffromdate=datetime.strptime(fromdate, '%b %d %Y %I:%M%p')
                print(type(fromdate))
                print(fromdate.strftime("%B %d, %Y"))
                last_month=fromdate.strftime("%B %d, %I:%M %p")+" To "+todate.strftime("%B %d, %I:%M %p")
                reseller = UserData.objects.filter(sponserId=currentuser,postId="User")
                #print(reseller)
                resellerlist=list()
                for i in reseller:
                    resellerdata={'username':i.username,'name':i.name}
                    resellerlist.append(resellerdata)
                #print(username)
                userdetails = UserData.objects.get(username=request.session["user"])
                vcloudtxns = vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate,sponser3__username=currentuser,type="Vcloud",sponser4__username=uuusername).order_by('-date')
                content=list()
                topuser=list()
                noofrecords=0
                productsum =0
                quantitysum =0
                profitsum =0
                count=0
                for i in vcloudtxns:
                    count=count+1
                    cost=i.denominations+i.margin1+i.margin2
                    productsum=productsum+(cost*i.quantity)
                    quantitysum=quantitysum+i.quantity
                    if(i.saleduser.username==username):
                        profit=0
                        #data3={'user':i.sponser2.name,'amount':(i.denominations*i.quantity)}
                        data={"id":i.id,"saleduser":i.sponser3.name,"role":i.sponser3.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                        content.append(data)
                        profitsum = profitsum+profit
                    else:
                        profit=i.margin3*i.quantity
                        data3={'user':i.sponser4.name,'amount':(cost*i.quantity)}
                        topuser.append(data3)
                        data={"id":i.id,"saleduser":i.sponser4.name,"role":i.sponser4.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                        content.append(data)
                        profitsum = profitsum+profit
                box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum,'noofrecords':count}
                brand = vcloudAssignments.objects.filter(assignedto=currentuser).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description','margin')
                product=list()
                print(brand)
                for i in brand:
                    print(i['brand__id'])
                    pd=vcloudProducts.objects.filter(brand=i['brand__id'],status=True).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
                    lpd=list(pd)
                    count=0
                    if not lpd:
                        pass
                        #print("Haiii")
                    else:
                        username=request.session["user"]
                        productcost=Decimal(lpd[0]['brand__denomination'])
                        print(productcost)
                        while(True):
                            userdet2=UserData.objects.filter(username=username).values('sponserId','postId')
                            print(userdet2)
                            margindet=vcloudAssignments.objects.filter(assignedto=username,brand__brand=i['brand__brand']).values('margin')
                            if(userdet2[0]['postId']=="Admin"):
                                break;
                            else:
                                print(margindet[0]['margin'])
                                productcost = Decimal(productcost)+Decimal(margindet[0]['margin'])
                                print(productcost)
                                username=userdet2[0]['sponserId']
                            count=int(count)+1
                        data={"brand":lpd[0]['brand__brand'],'rate':productcost}
                        product.append(data)
                        #print(content)
                print(product)
                list3=list()
                sorted_users = sorted(topuser, key=itemgetter('user'))

                for key, group in itertools.groupby(sorted_users, key=lambda x:x['user']):
                    amountsum=0
                    for g in group:
                        amountsum=amountsum+g["amount"]
                        #print(amountsum)
                    data5={'user':key,'amount':amountsum}
                    list3.append(data5)
                return render(request,"sub_reseller/vcloud/dashboard-vcloud.html",{'filterform':vcloudDashboardfilter,'reseller':resellerlist,'recenttransactions':content,'products':product,'user':userdetails,'topuser':list3,'last_month':last_month,'boxval':box_data})
            else:
                return redirect(subresellervcloudhomePage)
        else:
            return(subresellervcloudhomePage)
    else:
        return redirect(LoginPage)


def subresellervcloudaddUser(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"sub_reseller/vcloud/addUser.html",{'form':AddUserDataForm,'user':userdetails})
    else:
        return redirect(LoginPage)

def subresellervcloudnewUser(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = AddUserDataForm(request.POST or None)
            print(form.errors)
            if form.is_valid():
                username=form.cleaned_data.get("username")
                password=form.cleaned_data.get("password")
                hashkey = username+password
                hash = hashlib.sha256(hashkey.encode()).hexdigest()
                print(username)
                print(password)
                print(hash)
                sponser = request.session["user"]
                sponseruser=UserData.objects.get(username=sponser)
                Userdata=form.save(commit=False)
                Userdata.postId="User"
                Userdata.sponserId = sponseruser
                Userdata.status = True
                Userdata.balance = 0
                Userdata.targetAmt = 0
                Userdata.rentalAmt = 0
                Userdata.dcard_status = True
                Userdata.rcard_status = True
                Userdata.password = hash
                Userdata.save()
                messages.success(request, 'Successfully Added')
                return redirect(subresellervcloudaddUser)
            else:
                messages.warning(request, form.errors)
                userdetails = UserData.objects.get(username=request.session["user"])
                form = AddUserDataForm()
                return render(request,"sub_reseller/vcloud/addUser.html",{'form':AddUserDataForm,'user':userdetails})
        else:
            userdetails = UserData.objects.get(username=request.session["user"])
            form = AddUserDataForm()
            return render(request,"sub_reseller/vcloud/addUser.html",{'form':AddUserDataForm,'user':userdetails})
    else:
        return redirect(LoginPage)

def subresellervcloudviewUser(request):
    if request.session.has_key("user"):
        username = request.session["user"]
        resellers = UserData.objects.filter(postId="User",sponserId=username)
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"sub_reseller/vcloud/viewUser.html",{'resellers':resellers,'user':userdetails})
    else:
        return redirect(LoginPage)

def subresellervcloudprofile(request):
    if request.session.has_key("user"):
        user = request.session["user"]
        userDet = UserData.objects.get(username=user)
        return render(request,"sub_reseller/vcloud/editProfile.html",{'user':userDet})
    else:
        return redirect(LoginPage)

def subresellervcloudeditProfile(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            user = request.session["user"]
            name = request.POST.get('name', None)
            address = request.POST.get('address', None)
            email = request.POST.get('email', None)
            mobileno = request.POST.get('mobileno', None)
            userDet = UserData.objects.get(username=user)
            userDet.name = name
            userDet.address = address
            userDet.email = email
            userDet.mobileno = mobileno
            userDet.save()
            messages.success(request, 'Successfully Updated')
            return redirect(subresellervcloudprofile)
        else:
            messages.warning(request,'Internal Error Occured')
            return redirect(subresellervcloudprofile)
    else:
        return redirect(LoginPage)

def subresellervcloudbalanceTransfer(request):
    if request.session.has_key("user"):
        username = request.session["user"]
        userdetails = UserData.objects.get(username=request.session["user"])
        reseller = UserData.objects.filter(sponserId=username,postId="Sub_Reseller")
        fromsum = balanceTransactionReport.objects.filter(source=userdetails,category='BT').aggregate(Sum('amount'))
        tosum = balanceTransactionReport.objects.filter(destination=userdetails,category='BT').aggregate(Sum('amount'))
        bthist = balanceTransactionReport.objects.filter(source=userdetails).order_by('-date') | balanceTransactionReport.objects.filter(destination=userdetails).order_by('-date')
        return render(request,"sub_reseller/vcloud/balanceTransfer.html",{'form':balancetransferfilterform,'reseller':reseller,'bthist':bthist,'fromsum':fromsum['amount__sum'],'tosum':tosum['amount__sum'],'user':userdetails})
    else:
        return redirect(LoginPage)

def filtersubresellervcloudbtreport(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            form = balancetransferfilterform(request.POST or None)
            print(form.errors)
            if form.is_valid():
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                usertype=form.cleaned_data.get("usertype")
                susername=form.cleaned_data.get("username")
                username = request.session["user"]
                filter={'ffdate':fromdate,'ttdate':todate,'fuser':susername}
                userdetails = UserData.objects.get(username=request.session["user"])
                reseller = UserData.objects.filter(sponserId=username,postId="User")
                fromsum=None
                tosum=None
                bthist=None
                try:
                    if(susername == "Self"):
                        fromsum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails).aggregate(Sum('amount'))
                        tosum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdetails).aggregate(Sum('amount'))
                        bthist = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdetails)
                    elif(susername == "All"):
                        fromsum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails).aggregate(Sum('amount'))
                        tosum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdetails).aggregate(Sum('amount'))
                        bthist = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails)
                    elif(susername != "All"):
                        fromsum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__username=susername).aggregate(Sum('amount'))
                        tosum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdetails).aggregate(Sum('amount'))
                        bthist = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__username=susername)
                except:
                    pass
                return render(request,"sub_reseller/vcloud/balanceTransferReport.html",{'form':balancetransferfilterform,'reseller':reseller,'bthist':bthist,'fromsum':fromsum['amount__sum'],'tosum':tosum['amount__sum'],'user':userdetails,'filter':filter})
            else:
                return redirect(subresellervcloudbalanceTransferReport)
        else:
            return redirect(subresellervcloudbalanceTransferReport)
    else:
        return redirect(LoginPage)

def subresellervcloudSubmitBalanceTransfer(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            userType = request.POST.get('userType', None)
            user = request.POST.get('users', None)
            amount = request.POST.get('amount', None)
            userdet = UserData.objects.get(username=user)
            bal = userdet.balance
            newbal=bal+Decimal(amount)
            cdbal = userdet.targetAmt
            newcdbal = cdbal-Decimal(amount)
            userdet.targetAmt = newcdbal
            userdet.balance = newbal
            userdet.save()
            userdetails = UserData.objects.get(username=request.session["user"])
            btreport = balanceTransactionReport()
            btreport.source = userdetails
            btreport.destination = userdet
            btreport.category = "BT"
            btreport.pbalance = bal
            btreport.nbalance = newbal
            btreport.cramount = newcdbal
            btreport.amount = amount
            btreport.remarks = 'Added To Balance'
            btreport.save()
            messages.success(request, 'Successfully Updated The balance')
            return redirect(subresellervcloudbalanceTransfer)
            #userdata=UserData.objects.get(username=)
        else:
            messages.warning(request, 'Internal Error Occured')
            return redirect(subresellervcloudbalanceTransfer)
    else:
        return redirect(LoginPage)


def subresellervcloudaddPayment(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        phist=fundTransactionReport.objects.filter(source=userdetails).order_by('-date')
        return render(request,"sub_reseller/vcloud/addPayment.html",{'phist':phist,'user':userdetails})
    else:
        return redirect(LoginPage)

def subresellervcloudsubmitPayment(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            userType = request.POST.get('userType', None)
            user = request.POST.get('users', None)
            amount = request.POST.get('amount', None)
            remarks = request.POST.get('remarks', None)
            userdet = UserData.objects.get(username=user)
            obalance = userdet.targetAmt
            cdbal = userdet.targetAmt
            newcdbal = cdbal+Decimal(amount)
            userdet.targetAmt = newcdbal
            userdet.save()
            closeuser = UserData.objects.get(username=user)
            userdetails = UserData.objects.get(username=request.session["user"])
            ftreport=fundTransactionReport()
            ftreport.source = userdetails
            ftreport.destination = userdet
            ftreport.role = userType
            ftreport.obalance = obalance
            ftreport.cbalance = closeuser.targetAmt
            ftreport.amount = amount
            ftreport.balance = newcdbal
            ftreport.remarks = remarks
            ftreport.save()
            messages.success(request, 'Successfully Updated The balance')
            return redirect(subresellervcloudaddPayment)
        else:
            messages.warning(request, 'Internal Error Occured')
            return redirect(subresellervcloudaddPayment)
    else:
        return redirect(LoginPage)

def subresellervcloudbalanceTransferReport(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        reseller = UserData.objects.filter(sponserId=request.session["user"],postId="User")
        fromsum = balanceTransactionReport.objects.filter(source=userdetails,category='BT').aggregate(Sum('amount'))
        tosum = balanceTransactionReport.objects.filter(destination=userdetails,category='BT').aggregate(Sum('amount'))
        bthist = balanceTransactionReport.objects.filter(source=userdetails).order_by('-date') | balanceTransactionReport.objects.filter(destination=userdetails).order_by('-date')
        return render(request,"sub_reseller/vcloud/balanceTransferReport.html",{'form':balancetransferfilterform,'bthist':bthist,'fromsum':fromsum['amount__sum'],'tosum':tosum['amount__sum'],'user':userdetails,'reseller':reseller})
    else:
        return redirect(LoginPage)

def subresellervcloudpaymentReport(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        reseller = UserData.objects.filter(sponserId=request.session["user"],postId="User")
        phist = fundTransactionReport.objects.filter(source=userdetails).order_by('-date')|fundTransactionReport.objects.filter(destination=userdetails).order_by('-date')
        bsum = fundTransactionReport.objects.filter(source=userdetails).aggregate(Sum('amount'))
        return render(request,"sub_reseller/vcloud/paymentReport.html",{'form':paymentfilterform,'reseller':reseller,'phist':phist,'sum':bsum['amount__sum'],'user':userdetails})
    else:
        return redirect(LoginPage)

def filtersubresellervcloudpaymentreport(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            form = balancetransferfilterform(request.POST or None)
            print(form.errors)
            if form.is_valid():
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                usertype=form.cleaned_data.get("usertype")
                susername=form.cleaned_data.get("username")
                username = request.session["user"]
                filter={'ffdate':fromdate,'ttdate':todate,'fuser':susername}
                userdetails = UserData.objects.get(username=request.session["user"])
                reseller = UserData.objects.filter(sponserId=username,postId="User")
                bsum=None
                phist=None
                try:
                    if(susername=="Self"):
                        bsum = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails).aggregate(Sum('amount'))
                        phist = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdetails)
                        #print(phist)
                    elif(susername == "All"):
                        bsum = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails).aggregate(Sum('amount'))
                        phist = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails)
                        print(phist)
                    elif(susername != "All"):
                        bsum = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__username=susername).aggregate(Sum('amount'))
                        phist = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__username=susername)
                except Exception as e:
                    print(e)
                    pass
                return render(request,"sub_reseller/vcloud/paymentReport.html",{'form':paymentfilterform,'reseller':reseller,'phist':phist,'sum':bsum['amount__sum'],'user':userdetails,'filter':filter})
            else:
                return redirect(subresellervcloudpaymentReport)
        else:
            return redirect(subresellervcloudpaymentReport)
    else:
        return redirect(LoginPage)

def subresellervcloudreport(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        username=request.session["user"]
        last_month = datetime.today() - timedelta(days=1)
        vcloudtxns = vcloudtransactions.objects.filter(date__gte=last_month,sponser3__username=username).order_by('-date')
        #vcloudtxns = vcloudtransactions.objects.all().order_by('-date')
        reseller=UserData.objects.filter(sponserId=username,postId="User")
        resellerlist=list()
        vcbrand=vcloudBrands.objects.all()
        vcbrandlist=list()
        for b in vcbrand:
            branddata={'brand':b.brand}
            vcbrandlist.append(branddata)

        for i in reseller:
            resellerdata={'username':i.username,'name':i.name}
            resellerlist.append(resellerdata)
        content=list()
        noofrecords=0
        productsum =0
        quantitysum =0
        profitsum =0
        cost=0
        for i in vcloudtxns:
            cost=i.denominations+i.margin1+i.margin2
            productsum=productsum+(cost*i.quantity)
            quantitysum=quantitysum+i.quantity
            if(i.saleduser.username==username):
                profit=0
                data={"id":i.id,"saleduser":i.sponser3.name,"role":i.sponser3.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                content.append(data)
                profitsum = profitsum+profit
            else:
                profit=(i.margin3*i.quantity)
                data={"id":i.id,"saleduser":i.sponser4.name,"role":i.sponser4.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                content.append(data)
                profitsum = profitsum+profit

        box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum}
        return render(request,"sub_reseller/vcloud/vcloudreport.html",{'filterform':vcloudreportfilterform,'products':content,'user':userdetails,'reseller':resellerlist, 'brand':vcbrandlist,'box':box_data,'date':last_month})
    else:
        return redirect(LoginPage)

def filtersubresellervcloud_report(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            form = vcloudreportfilterform(request.POST or None)
            print(form.errors)
            if form.is_valid():
                username=request.session["user"]
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                usertype=form.cleaned_data.get("usertype")
                fusername=form.cleaned_data.get("username")
                type=form.cleaned_data.get("type")
                brand=form.cleaned_data.get("brand")
                #print(brand,fusername)
                fuser=''
                if(fusername!='All'):
                    filterdata=UserData.objects.get(username=fusername)
                    fuser=filterdata.name
                else:
                    fuser=fusername
                filter={'ffdate':fromdate,'ttdate':todate,'fuser':fuser}
                userdetails = UserData.objects.get(username=request.session["user"])
                reseller=UserData.objects.filter(sponserId=username,postId="User")
                resellerlist=list()
                vcbrand=vcloudBrands.objects.all()
                vcbrandlist=list()
                for b in vcbrand:
                    branddata={'brand':b.brand}
                    vcbrandlist.append(branddata)

                for i in reseller:
                    resellerdata={'username':i.username,'name':i.name}
                    resellerlist.append(resellerdata)

                content=list()
                noofrecords = 0
                productsum = 0
                quantitysum = 0
                profitsum = 0
                vcloudtxns=vcloudtransactions()
                try:
                    print(usertype)
                    print(fusername)
                    print(type)
                    print(brand)
                    if(fusername=="All" and type=="All" and brand=="All"):
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser3__username=username).order_by('-date')
                        print("One")
                    elif(fusername=="All" and type=="All" and brand !="All"):
                        print("TWo")
                        vcloudtxns==vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser3__username=username, brand=brand).order_by('-date')
                    elif(fusername=="All" and type !="All" and brand =="All"):
                        print("Three")
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser3__username=username, type=type).order_by('-date')
                    elif(fusername=="All" and type !="All" and brand !="All"):
                        print("four")
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser3__username=username, brand=brand).order_by('-date')
                    elif(fusername!="All" and type !="All" and brand !="All"):
                        print('five')
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, type=type, sponser3__username=username, sponser4__username=fusername, brand=brand).order_by('-date')
                    elif(fusername =="All" and type =="All" and brand !="All"):
                        print('Six')
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser3__username=username).order_by('-date')
                    elif(fusername =="All" and type =="All" and brand =="All"):
                        print('Six')
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser3__username=username, sponser4__postId=usertype).order_by('-date')
                    elif(fusername !="All" and type =="All" and brand =="All"):
                        print('Six')
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser3__username=username, sponser4__username=fusername).order_by('-date')
                    elif(fusername !="All" and type =="All" and brand =="All"):
                        print('Six')
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser3__username=username, sponser4__username=fusername).order_by('-date')
                    else:
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser3__username=username, sponser4__username=fusername,brand=brand).order_by('-date')
                    print(vcloudtxns)

                    for i in vcloudtxns:
                        cost=i.denominations+i.margin1+i.margin2
                        productsum=productsum+(cost*i.quantity)
                        quantitysum=quantitysum+i.quantity
                        if(i.saleduser.username==username):
                            profit=0
                            data={"id":i.id,"saleduser":i.sponser3.name,"role":i.sponser3.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                            content.append(data)
                            profitsum = profitsum+profit
                        else:
                            profit=(i.margin3*i.quantity)
                            data={"id":i.id,"saleduser":i.sponser4.name,"role":i.sponser4.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                            content.append(data)
                            profitsum = profitsum+profit
                except:
                    pass
                box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum}
                return render(request,"sub_reseller/vcloud/vcloudreport.html",{'filterform':vcloudreportfilterform,'products':content,'user':userdetails,'reseller':resellerlist, 'brand':vcbrandlist,'box':box_data,'filter':filter})
            else:
                return redirect(subresellervcloudreport)
        else:
            return redirect(subresellervcloudreport)
    else:
        return redirect(LoginPage)

def subresellervcloudStore(request):
    if request.session.has_key("user"):
        username=request.session["user"]
        ads = adverisements.objects.filter(adtype="Image",usertype="Sub_Reseller",ctype="Vcloud").order_by('-id')[:10]
        pdcts = vcloudAssignments.objects.filter(assignedto=username,brand__category="card with cutting").order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description','margin')
        data=dict()
        content = []
        for i in pdcts:
            try:
                pd=vcloudProducts.objects.filter(brand=i['brand__id'],status=True).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
                lpd=list(pd)
                count=0
                if not lpd:
                    pass
                else:
                    username=request.session["user"]
                    productcost=Decimal(lpd[0]['brand__denomination'])
                    print(productcost)
                    while(True):
                        print(i['brand__brand'])
                        userdet2=UserData.objects.filter(username=username).values('sponserId','postId')
                        print(userdet2)
                        print(username)
                        margindet=vcloudAssignments.objects.filter(assignedto=username,brand__brand=i['brand__brand']).values('margin')
                        print(margindet)
                        if(userdet2[0]['postId']=="Admin"):
                            break;
                        else:
                            print(margindet[0]['margin'])
                            productcost = Decimal(productcost)+Decimal(margindet[0]['margin'])
                            print(productcost)
                            username=userdet2[0]['sponserId']
                        count=int(count)+1
                    data={"brand_id":lpd[0]['brand__id'],"brand__brand":lpd[0]['brand__brand'],'productcount':lpd[0]['productcount'],'brand__logo':lpd[0]['brand__logo'],'brand__denomination':productcost,'brand__currency':lpd[0]['brand__currency'],'brand__description':lpd[0]['brand__description']}
                    content.append(data)
                    print(content)
            except Exception as e:
                print(e)
                pass
        buttonlist=["Cutting","Non Cutting"]
        buttonclass=["btn-warning","btn-success"]
        btnlist = zip(buttonlist, buttonclass)
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"sub_reseller/vcloud/vcloudStore.html",{'pdcts':content,'btnlist':btnlist,'user':userdetails,'ads':ads})
    else:
        return redirect(LoginPage)

def subresellerfilteredvcloudstore(request,brandtype):
    if request.session.has_key("user"):
        username=request.session["user"]
        buttonclass=[]
        ads = adverisements.objects.filter(adtype="Image",usertype="Sub_Reseller",ctype="Vcloud").order_by('-id')[:10]
        if(brandtype=="Cutting"):
            pdcts = vcloudAssignments.objects.filter(assignedto=username,brand__category="card with cutting").order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
            data=dict()
            content = []
            for i in pdcts:
                try:
                    pd=vcloudProducts.objects.filter(brand=i['brand__id'],status=True).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
                    lpd=list(pd)
                    #print(lpd)
                    #print(productcost)
                    count=0
                    if not lpd:
                        pass;
                        #print("Haiii")
                    else:
                        username=request.session["user"]
                        productcost=Decimal(lpd[0]['brand__denomination'])
                        print(productcost)
                        while(True):
                            userdet2=UserData.objects.filter(username=username).values('sponserId','postId')
                            print(userdet2)
                            margindet=vcloudAssignments.objects.filter(assignedto=username,brand__brand=i['brand__brand']).values('margin')
                            if(userdet2[0]['postId']=="Admin"):
                                break;
                            else:
                                print(margindet[0]['margin'])
                                productcost = Decimal(productcost)+Decimal(margindet[0]['margin'])
                                print(productcost)
                                username=userdet2[0]['sponserId']
                            count=int(count)+1
                        data={"brand_id":lpd[0]['brand__id'],"brand__brand":lpd[0]['brand__brand'],'productcount':lpd[0]['productcount'],'brand__logo':lpd[0]['brand__logo'],'brand__denomination':productcost,'brand__currency':lpd[0]['brand__currency'],'brand__description':lpd[0]['brand__description']}
                        content.append(data)
                        print(content)
                except Exception as e:
                    print(e)
                    pass
            buttonclass=["btn-warning","btn-success"]
        else:
            pdcts = vcloudAssignments.objects.filter(assignedto=username,brand__category="card without cutting").order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
            data=dict()
            content = []
            for i in pdcts:
                try:
                    pd=vcloudProducts.objects.filter(brand=i['brand__id'],status=True).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
                    lpd=list(pd)
                    #print(lpd)
                    #print(productcost)
                    count=0
                    if not lpd:
                        pass
                        #print("Haiii")
                    else:
                        username=request.session["user"]
                        productcost=Decimal(lpd[0]['brand__denomination'])
                        print(productcost)
                        while(True):
                            userdet2=UserData.objects.filter(username=username).values('sponserId','postId')
                            print(userdet2)
                            margindet=vcloudAssignments.objects.filter(assignedto=username,brand__brand=i['brand__brand']).values('margin')
                            if(userdet2[0]['postId']=="Admin"):
                                break;
                            else:
                                print(margindet[0]['margin'])
                                productcost = Decimal(productcost)+Decimal(margindet[0]['margin'])
                                print(productcost)
                                username=userdet2[0]['sponserId']
                            count=int(count)+1
                        data={"brand_id":lpd[0]['brand__id'],"brand__brand":lpd[0]['brand__brand'],'productcount':lpd[0]['productcount'],'brand__logo':lpd[0]['brand__logo'],'brand__denomination':productcost,'brand__currency':lpd[0]['brand__currency'],'brand__description':lpd[0]['brand__description']}
                        content.append(data)
                        print(content)
                except Exception as e:
                    print(e)
                    pass
            buttonclass=["btn-success","btn-warning"]
        buttonlist=["Cutting","Non Cutting"]
        btnlist = zip(buttonlist, buttonclass)
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"sub_reseller/vcloud/vcloudStore.html",{'pdcts':content,'btnlist':btnlist,'user':userdetails,'ads':ads})
    else:
        return redirect(LoginPage)

def subresellersaveassignVcloudBrands(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            try:
                reseller = request.POST.get('username', None)
                values = request.POST.get('values', None)
                states = request.POST.get('states', None)
                brands = request.POST.get('brands', None)
                margins = request.POST.get('margins', None)
                v = values.split(',')
                s = states.split(',')
                b = brands.split(',')
                m = margins.split(',')
                username = request.session["user"]
                assignedby = UserData.objects.get(username=username)
                assignedto = UserData.objects.get(username=reseller)
                for i in range(0,len(s)):
                    if(int(s[i])==0):
                        print(True)
                        brandid=b[int(i)]
                        brdet=vcloudBrands.objects.get(id=brandid)
                        print(brdet)
                        try:
                            vdt = vcloudAssignments.objects.get(brand=brdet,assignedby=assignedby,assignedto=assignedto)
                            vdt.delete()
                            vadt = vcloudAssignments.objects.get(brand=brdet,assignedby=assignedto)
                            print(vadt)
                            for i in vadt:
                                try:
                                    ud = vcloudAssignments.objects.filter(brand=brdet,assignedby=i.assignedto)
                                    ud.delete()
                                except Exception as e:
                                    print("inner "+str(e))
                            vadt.delete()
                        except vcloudAssignments.DoesNotExist:
                            print("Error")
                    else:
                        print(False)
                        brandid=b[int(i)]
                        brdet=vcloudBrands.objects.get(id=brandid)
                        try:
                            assdet = vcloudAssignments.objects.get(brand=brdet,assignedby=assignedby,assignedto=assignedto)
                            assdet.margin = Decimal(v[int(i)])
                            assdet.save()
                        except vcloudAssignments.DoesNotExist:
                            vass = vcloudAssignments()
                            vass.brand=brdet
                            vass.assignedto=assignedto
                            vass.assignedby=assignedby
                            vass.margin = Decimal(v[int(i)])
                            vass.save()
                data={"status":"Success"}
                return JsonResponse(data)
            except:
                return JsonResponse({"status":"Error"})
        else:
            pass
    else:
        return redirect(LoginPage)

def subgetvcloudproductcost(brand,username):
    print(brand)
    prdcts=vcloudBrands.objects.get(brand=brand)
    print(prdcts)
    prdctcost = Decimal(prdcts.denomination)
    margins=0
    while(True):
        userdet = UserData.objects.filter(username=username).values('sponserId','postId')
        pdct = vcloudAssignments.objects.filter(assignedto=username, brand__brand=brand).values('margin')
        if(pdct):
            if(userdet[0]['postId']=="Admin"):
                break;
            else:
                prdctcost = prdctcost+Decimal(pdct[0]['margin'])
            username=userdet[0]['sponserId']
        else:
            break;
    print(prdctcost)
    return prdctcost

def subresellerassignVcloudBrands(request):
    if request.session.has_key("user"):
        brands = vcloudAssignments.objects.filter(assignedto=request.session["user"]).values('brand','brand__brand')
        username=request.session["user"]
        costlist=list()
        brandlist=list()
        for j in brands:
            try:
                prdcts=vcloudBrands.objects.get(brand=j['brand__brand'])
                #prdcts=vcloudProducts.objects.filter(brand__brand=j['brand__brand'],status=True).order_by('brand').annotate(productcount=Count('brand')).values('brand','brand__brand','brand__id','brand__denomination','brand__logo','brand__description','brand__currency','brand__category')
                if(prdcts):
                    cost=subgetvcloudproductcost(j['brand__brand'],username)
                    #costlist.append(cost)
                    data={'cost':cost,'brand':prdcts.id,'brand__brand':prdcts.brand,'brand__id':prdcts.id,'brand__denomination':prdcts.denomination,'brand__logo':prdcts.logo.url,'brand__description':prdcts.description,'brand__currency':prdcts.currency,'brand__category':prdcts.category}
                    brandlist.append(data)
                else:
                    pass
            except vcloudProducts.DoesNotExist:
                pass;
        resellers = UserData.objects.filter(postId="User",sponserId=request.session["user"])
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"sub_reseller/vcloud/assignVcloudBrands.html",{'brands':brands,'products':brandlist,'resellers':resellers,'user':userdetails})
    else:
        return redirect(LoginPage)


def subresellerviewbrands(request):
    if request.session.has_key("user"):
        username = request.session["user"]
        vcdprod=vcloudBrands.objects.all()
        resultlist=list()
        statuslist=list()
        for i in vcdprod:
            vca=vcloudAssignments.objects.filter(assignedto=username,brand__brand=i.brand)
            if not vca:
                statuslist.append(False)
            else:
                statuslist.append(True)
        vcd=list(vcdprod)
        print(vcd)
        print(statuslist)
        #print(data)
        ldb=zip(vcd,statuslist)
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"sub_reseller/vcloud/viewBrands.html",{'pdcts':list(ldb),'user':userdetails})
    else:
        return redirect(LoginPage)

def check_balance(username,brand):
    userbal=UserData.objects.filter(username=username).only('balance')
    usermargin=vcloudAssignments.objects.filter(assignedto=username,brand__brand=brand).values('margin')



def sub_buy_vcloud_brands(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            username=request.session["user"]
            brand = request.POST.get('brandid', None)
            quantity = request.POST.get('quantity', None)
            amt = request.POST.get('amt', None)
            branddet=vcloudBrands.objects.get(brand=brand)
            userdet=UserData.objects.get(username=request.session["user"])
            #checkqty = vcloudProducts.objects.filter(brand__brand=brand, status=True).exclude(productstatus=1).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('productcount')
            ctime=datetime.now()
            time = timedelta(minutes = 5)
            now_minus_5 = ctime - time
            checkqty=vcloudProducts.objects.filter(Q(brand__brand=brand) & Q(status=True) & (Q(sdate__isnull=True) | Q(sdate__lte=now_minus_5))).values('brand').annotate(productcount=Count('brand')).values('productcount')
            print(checkqty)
            needamt=0;
            result=list()
            content=dict()
            licheckqty=list(checkqty)
            brand_id=0
            deno=0
            if(licheckqty[0]['productcount'] >= int(quantity)):
                usertype=''
                marginlist=list()
                margins=0
                count=0;
                flag=True
                prdct_id=''
                mllist=list()
                sponserlist=list()
                prdctdet = vcloudProducts.objects.filter(Q(brand__brand=brand) & Q(status=True) & (Q(sdate__isnull=True) | Q(sdate__lte=now_minus_5)))[:int(quantity)]
                ctime = datetime.now()
                for i in prdctdet:
                    i.productstatus=1
                    i.suser = userdet
                    i.sdate = ctime
                    i.save()
                count=0
                admin=''
                while(True):
                    userdet2=UserData.objects.filter(username=username).values('sponserId','postId','balance')
                    margindet=vcloudAssignments.objects.filter(assignedto=username,brand__brand=brand).values('margin')
                    if(userdet2[0]['postId']=="Admin"):
                        admin=username
                        break;
                    else:
                        cost=Decimal(amt)
                        prdctcost = (cost*Decimal(quantity))-(Decimal(margins)*Decimal(quantity))
                        margins=margins+Decimal(margindet[0]['margin'])
                        #print(prdctcost)
                        #print(cost)
                        if(userdet2[0]['balance']>=prdctcost):
                            data={'margin':margindet[0]['margin'],'balance':userdet2[0]['balance'],'username':username,'prdctcost':prdctcost}
                            marginlist.append(data)
                            mllist.append(margindet[0]['margin'])
                            sponserlist.append(username)
                        else:
                            flag=False
                            print(flag)
                            break;
                    username=userdet2[0]['sponserId']
                if(flag):
                    try:
                        prdctcddet=vcloudProducts.objects.filter(brand__brand=brand,status=True,productstatus=1,suser=userdet,sdate=ctime)[:int(quantity)]
                        for h in prdctcddet:
                            h.status=False
                            h.save()
                            #print(h.username)
                            brand_id=h.brand.id
                            deno=h.brand.denomination
                            prdct_id=prdct_id+""+str(h.id)+","
                            res={"productid":h.id,"carduname":h.username,'brand':h.brand.brand,'brand_logo':h.brand.logo.url,'password':h.password,'status':h.status,'suser':username,'sdate':h.sdate}
                            result.append(res)

                        ml=marginlist[::-1]
                        for k in ml:
                            uname = k['username']
                            margin = k['margin']
                            balance = k['balance']
                            pcost = k['prdctcost']
                            cb=Decimal(balance)-Decimal(pcost)
                            userd=UserData.objects.get(username=uname)
                            userd.balance=cb
                            userd.save()
                        mllen = len(mllist)
                        vcrep=vcloudtransactions()
                        vcrep.saleduser = userdet
                        vcrep.brand = brand
                        vcrep.type = "Vcloud"
                        vcrep.brand_id = brand_id
                        vcrep.product_id = prdct_id
                        vcrep.quantity = quantity
                        vcrep.amount = amt
                        vcrep.rtype = "Web"
                        vcrep.denominations = deno
                        ms = mllist[::-1]
                        mu = sponserlist[::-1]
                        print(ms)
                        print(admin)
                        ad=UserData.objects.get(username=admin)
                        if(mllen==1):
                            vcrep.margin1=ms[0]
                            vcrep.sponser1=ad
                            vcrep.sponser2=UserData.objects.get(username=sponserlist[0])
                        elif(mllen==2):
                            vcrep.margin1=ms[0]
                            vcrep.margin2=ms[1]
                            vcrep.sponser1=ad
                            vcrep.sponser2=UserData.objects.get(username=sponserlist[1])
                            vcrep.sponser3=UserData.objects.get(username=sponserlist[0])
                        else:
                            vcrep.margin1=ms[0]
                            vcrep.margin2=ms[1]
                            vcrep.margin3=ms[2]
                            vcrep.sponser1=ad
                            vcrep.sponser2=UserData.objects.get(username=sponserlist[2])
                            vcrep.sponser3=UserData.objects.get(username=sponserlist[1])
                            vcrep.sponser4=UserData.objects.get(username=sponserlist[0])
                        vcrep.save()
                        obj = vcloudtransactions.objects.latest('id')
                        print(obj.id)
                        content["data"] = result
                        content["res_status"]="success"
                        content["trid"]=obj.id
                    except:
                        content["res_status"]="Failed"
                else:
                    for i in prdctdet:
                        i.suser=None
                        i.save()
                    content["res_status"]="Failed"
            return JsonResponse(content,safe=False)
        else:
            return redirect(subresellervcloudStore)
    else:
        return redirect(LoginPage)

def subprintLayout(request):
    return render(request,"sub_reseller/printLayout.html")

def subeditresellerProfilevcloud(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            user = request.session["user"]
            name = request.POST.get('name', None)
            address = request.POST.get('address', None)
            email = request.POST.get('email', None)
            mobileno = request.POST.get('mobileno', None)
            userDet = UserData.objects.get(username=user)
            userDet.name = name
            userDet.address = address
            userDet.email = email
            userDet.mobileno = mobileno
            userDet.save()
            messages.success(request, 'Successfully Updated')
            return redirect(resellerprofiledcard)
        else:
            messages.warning(request,'Internal Error Occured')
            return redirect(resellerprofiledcard)
    else:
        return redirect(LoginPage)

#________________DCARD_______________

def subresellerDcardDashboard(request):
    if request.session.has_key("user"):
        username = request.session["user"]
        #print(last_month)
        reseller = UserData.objects.filter(sponserId=username,postId="User")
        #print(reseller)
        resellerlist=list()
        for i in reseller:
            resellerdata={'username':i.username,'name':i.name}
            resellerlist.append(resellerdata)
        username = request.session["user"]
        type = request.session["usertype"]
        try:
            user = UserData.objects.get(username = username, postId = type)
        except UserData.DoesNotExist:
            return redirect(LoginPage)
        userdetails = UserData.objects.get(username=request.session["user"])
        username=request.session["user"]
        last_month = datetime.today() - timedelta(days=1)
        vcloudtxns = vcloudtransactions.objects.filter(date__gte=last_month,sponser3__username=username,type="Dcard").order_by('-date')
        content=list()
        topuser=list()
        noofrecords=0
        productsum =0
        quantitysum =0
        profitsum =0
        count=0
        for i in vcloudtxns:
            count=count+1
            cost=i.denominations+i.margin1+i.margin2
            productsum=productsum+(cost*i.quantity)
            quantitysum=quantitysum+i.quantity
            if(i.saleduser.username==username):
                profit=0
                #data3={'user':i.sponser2.name,'amount':(i.denominations*i.quantity)}
                data={"id":i.id,"saleduser":i.sponser3.name,"role":i.sponser3.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                content.append(data)
                profitsum = profitsum+profit
            else:
                profit=i.margin3*i.quantity
                data3={'user':i.sponser4.name,'amount':(cost*i.quantity)}
                topuser.append(data3)
                data={"id":i.id,"saleduser":i.sponser4.name,"role":i.sponser4.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                content.append(data)
                profitsum = profitsum+profit
        box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum,'noofrecords':count}
        brand = datacardAssignments.objects.filter(assignedto=username).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description','margin')
        product=list()
        for i in brand:
            pd=datacardproducts.objects.filter(brand=i['brand__id'], status=True).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
            lpd=list(pd)
            count=0
            if not lpd:
                pass;
                #break;
                #print("Haiii")
            else:
                username=request.session["user"]
                productcost=Decimal(lpd[0]['brand__denomination'])
                print(productcost)
                while(True):
                    userdet2=UserData.objects.filter(username=username).values('sponserId','postId')
                    print(userdet2)
                    margindet=datacardAssignments.objects.filter(assignedto=username,brand__brand=i['brand__brand']).values('margin')
                    if(userdet2[0]['postId']=="Admin"):
                        break;
                    else:
                        print(margindet[0]['margin'])
                        productcost = Decimal(productcost)+Decimal(margindet[0]['margin'])
                        print(productcost)
                        username=userdet2[0]['sponserId']
                    count=int(count)+1
                data={"brand":lpd[0]['brand__brand'],'rate':productcost}
                product.append(data)
                #print(content)

        list3=list()
        sorted_users = sorted(topuser, key=itemgetter('user'))

        for key, group in itertools.groupby(sorted_users, key=lambda x:x['user']):
            amountsum=0
            for g in group:
                amountsum=amountsum+g["amount"]
                #print(amountsum)
            data5={'user':key,'amount':amountsum}
            list3.append(data5)
        return render(request,"sub_reseller/dcard/dashboard-dcard.html",{'filterform':dcardDashboardfilter,'reseller':resellerlist,'recenttransactions':content,'products':product,'user':user,'topuser':list3,'last_month':last_month,'boxval':box_data})
    else:
        return redirect(LoginPage)

def filtersubresellerDcardDashboard(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = dcardDashboardfilter(request.POST or None)
            print(form.errors)
            if form.is_valid():
                currentuser=request.session["user"]
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                usertype=form.cleaned_data.get("usertype")
                uuusername=form.cleaned_data.get("username")
                #mffromdate=datetime.strptime(fromdate, '%b %d %Y %I:%M%p')
                print(type(fromdate))
                print(fromdate.strftime("%B %d, %Y"))
                last_month=fromdate.strftime("%B %d, %I:%M %p")+" To "+todate.strftime("%B %d, %I:%M %p")
                reseller = UserData.objects.filter(sponserId=currentuser,postId="Sub_Reseller")
                #print(reseller)
                resellerlist=list()
                for i in reseller:
                    resellerdata={'username':i.username,'name':i.name}
                    resellerlist.append(resellerdata)
                #print(username)
                userdetails = UserData.objects.get(username=request.session["user"])
                vcloudtxns = vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate,sponser3__username=currentuser,type="Dcard",sponser4__username=uuusername).order_by('-date')
                content=list()
                topuser=list()
                noofrecords=0
                productsum =0
                quantitysum =0
                profitsum =0
                count=0
                for i in vcloudtxns:
                    count=count+1
                    cost=i.denominations+i.margin1+i.margin2
                    productsum=productsum+(cost*i.quantity)
                    quantitysum=quantitysum+i.quantity
                    if(i.saleduser.username==username):
                        profit=0
                        #data3={'user':i.sponser2.name,'amount':(i.denominations*i.quantity)}
                        data={"id":i.id,"saleduser":i.sponser3.name,"role":i.sponser3.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                        content.append(data)
                        profitsum = profitsum+profit
                    else:
                        profit=i.margin3*i.quantity
                        data3={'user':i.sponser4.name,'amount':(cost*i.quantity)}
                        topuser.append(data3)
                        data={"id":i.id,"saleduser":i.sponser4.name,"role":i.sponser4.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                        content.append(data)
                        profitsum = profitsum+profit
                box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum,'noofrecords':count}
                brand = datacardAssignments.objects.filter(assignedto=currentuser).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description','margin')
                product=list()
                print(brand)
                for i in brand:
                    print(i['brand__id'])
                    pd=datacardproducts.objects.filter(brand=i['brand__id'],status=True).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
                    lpd=list(pd)
                    count=0
                    if not lpd:
                        pass
                        #print("Haiii")
                    else:
                        username=request.session["user"]
                        productcost=Decimal(lpd[0]['brand__denomination'])
                        print(productcost)
                        while(True):
                            userdet2=UserData.objects.filter(username=username).values('sponserId','postId')
                            print(userdet2)
                            margindet=datacardAssignments.objects.filter(assignedto=username,brand__brand=i['brand__brand']).values('margin')
                            if(userdet2[0]['postId']=="Admin"):
                                break;
                            else:
                                print(margindet[0]['margin'])
                                productcost = Decimal(productcost)+Decimal(margindet[0]['margin'])
                                print(productcost)
                                username=userdet2[0]['sponserId']
                            count=int(count)+1
                        data={"brand":lpd[0]['brand__brand'],'rate':productcost}
                        product.append(data)
                        #print(content)
                print(product)
                list3=list()
                sorted_users = sorted(topuser, key=itemgetter('user'))

                for key, group in itertools.groupby(sorted_users, key=lambda x:x['user']):
                    amountsum=0
                    for g in group:
                        amountsum=amountsum+g["amount"]
                        #print(amountsum)
                    data5={'user':key,'amount':amountsum}
                    list3.append(data5)
                return render(request,"subreseller/dcard/dashboard-dcard.html",{'filterform':vcloudDashboardfilter,'reseller':resellerlist,'recenttransactions':content,'products':product,'user':userdetails,'topuser':list3,'last_month':last_month,'boxval':box_data})
            else:
                return redirect(subresellerDcardDashboard)
        else:
            return(subresellerDcardDashboard)
    else:
        return redirect(LoginPage)

def subresellerprofiledcard(request):
    if request.session.has_key("user"):
        user = request.session["user"]
        userDet = UserData.objects.get(username=user)
        return render(request,"sub_reseller/dcard/editProfile.html",{'user':userDet})
    else:
        return redirect(LoginPage)

def subreselleraddResellerDcard(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"sub_reseller/dcard/addReseller.html",{'form':AddUserDataForm,'user':userdetails})
    else:
        return redirect(LoginPage)

def subreselleraddUserDcard(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"sub_reseller/dcard/addUser.html",{'form':AddUserDataForm,'user':userdetails})
    else:
        return redirect(LoginPage)

def subresellerviewResellerDcard(request):
    if request.session.has_key("user"):
        resellers = UserData.objects.filter(sponserId=request.session["user"],postId="Sub_Reseller")
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"sub_reseller/dcard/viewResellers.html",{'resellers':resellers,'user':userdetails})
    else:
        return redirect(LoginPage)

def subresellerviewUserDcard(request):
    if request.session.has_key("user"):
        user = request.session["user"]
        resellers = UserData.objects.filter(postId="User",sponserId=user)
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"sub_reseller/dcard/viewUser.html",{'resellers':resellers,'user':userdetails})
    else:
        return redirect(LoginPage)

def subresellerbalanceTransferDcard(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        bthist=balanceTransactionReport.objects.filter(source=userdetails,category="BT").order_by('-date')
        #print(bthist)
        return render(request,"sub_reseller/dcard/balanceTransfer.html",{'bthist':bthist,'user':userdetails})
    else:
        return redirect(LoginPage)

def subreselleraddPaymentDcard(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        phist=fundTransactionReport.objects.filter(source=userdetails).order_by('-date')
        return render(request,"sub_reseller/dcard/addPayment.html",{'phist':phist})
    else:
        return redirect(LoginPage)

def subresellerdatacardreport(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        username=request.session["user"]
        last_month = datetime.today() - timedelta(days=1)
        vcloudtxns = vcloudtransactions.objects.filter(date__gte=last_month,sponser3__username=username).order_by('-date')
        #vcloudtxns = vcloudtransactions.objects.all().order_by('-date')
        reseller=UserData.objects.filter(sponserId=username,postId="User")
        resellerlist=list()
        vcbrand=vcloudBrands.objects.all()
        vcbrandlist=list()
        for b in vcbrand:
            branddata={'brand':b.brand}
            vcbrandlist.append(branddata)

        for i in reseller:
            resellerdata={'username':i.username,'name':i.name}
            resellerlist.append(resellerdata)
        content=list()
        noofrecords=0
        productsum =0
        quantitysum =0
        profitsum =0
        cost=0
        for i in vcloudtxns:
            cost=i.denominations+i.margin1+i.margin2
            productsum=productsum+(cost*i.quantity)
            quantitysum=quantitysum+i.quantity
            if(i.saleduser.username==username):
                profit=0
                data={"id":i.id,"saleduser":i.sponser3.name,"role":i.sponser3.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                content.append(data)
                profitsum = profitsum+profit
            else:
                profit=(i.margin3*i.quantity)
                data={"id":i.id,"saleduser":i.sponser4.name,"role":i.sponser4.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                content.append(data)
                profitsum = profitsum+profit

        box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum}
        return render(request,"sub_reseller/dcard/dcardreport.html",{'filterform':vcloudreportfilterform,'products':content,'user':userdetails,'reseller':resellerlist, 'brand':vcbrandlist,'box':box_data,'date':last_month})
    else:
        return redirect(LoginPage)

def filtersubresellerdcard_report(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            form = vcloudreportfilterform(request.POST or None)
            print(form.errors)
            if form.is_valid():
                username=request.session["user"]
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                usertype=form.cleaned_data.get("usertype")
                fusername=form.cleaned_data.get("username")
                type=form.cleaned_data.get("type")
                brand=form.cleaned_data.get("brand")
                #print(brand,fusername)
                fuser=''
                if(fusername!='All'):
                    filterdata=UserData.objects.get(username=fusername)
                    fuser=filterdata.name
                else:
                    fuser=fusername
                filter={'ffdate':fromdate,'ttdate':todate,'fuser':fuser}
                userdetails = UserData.objects.get(username=request.session["user"])
                reseller=UserData.objects.filter(sponserId=username,postId="User")
                resellerlist=list()
                vcbrand=vcloudBrands.objects.all()
                vcbrandlist=list()
                for b in vcbrand:
                    branddata={'brand':b.brand}
                    vcbrandlist.append(branddata)

                for i in reseller:
                    resellerdata={'username':i.username,'name':i.name}
                    resellerlist.append(resellerdata)

                content=list()
                noofrecords = 0
                productsum = 0
                quantitysum = 0
                profitsum = 0
                vcloudtxns=vcloudtransactions()
                try:
                    print(usertype)
                    print(fusername)
                    print(type)
                    print(brand)
                    if(fusername=="All" and type=="All" and brand=="All"):
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser3__username=username).order_by('-date')
                        print("One")
                    elif(fusername=="All" and type=="All" and brand !="All"):
                        print("TWo")
                        vcloudtxns==vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser3__username=username, brand=brand).order_by('-date')
                    elif(fusername=="All" and type !="All" and brand =="All"):
                        print("Three")
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser3__username=username, type=type).order_by('-date')
                    elif(fusername=="All" and type !="All" and brand !="All"):
                        print("four")
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser3__username=username, brand=brand).order_by('-date')
                    elif(fusername!="All" and type !="All" and brand !="All"):
                        print('five')
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, type=type, sponser3__username=username, sponser4__username=fusername, brand=brand).order_by('-date')
                    elif(fusername =="All" and type =="All" and brand !="All"):
                        print('Six')
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser3__username=username).order_by('-date')
                    elif(fusername =="All" and type =="All" and brand =="All"):
                        print('Six')
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser3__username=username, sponser4__postId=usertype).order_by('-date')
                    elif(fusername !="All" and type =="All" and brand =="All"):
                        print('Six')
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser3__username=username, sponser4__username=fusername).order_by('-date')
                    elif(fusername !="All" and type =="All" and brand =="All"):
                        print('Six')
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser3__username=username, sponser4__username=fusername).order_by('-date')
                    else:
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser3__username=username, sponser4__username=fusername,brand=brand).order_by('-date')
                    print(vcloudtxns)

                    for i in vcloudtxns:
                        cost=i.denominations+i.margin1+i.margin2
                        productsum=productsum+(cost*i.quantity)
                        quantitysum=quantitysum+i.quantity
                        if(i.saleduser.username==username):
                            profit=0
                            data={"id":i.id,"saleduser":i.sponser3.name,"role":i.sponser3.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                            content.append(data)
                            profitsum = profitsum+profit
                        else:
                            profit=(i.margin3*i.quantity)
                            data={"id":i.id,"saleduser":i.sponser4.name,"role":i.sponser4.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                            content.append(data)
                            profitsum = profitsum+profit
                except:
                    pass
                box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum}
                return render(request,"sub_reseller/dcard/dcardreport.html",{'filterform':vcloudreportfilterform,'products':content,'user':userdetails,'reseller':resellerlist, 'brand':vcbrandlist,'box':box_data,'filter':filter})
            else:
                return redirect(subresellerdatacardreport)
        else:
            return redirect(subresellerdatacardreport)
    else:
        return redirect(LoginPage)

def subresellerbTReportDcard(request):
    if request.session.has_key("user"):
        username = request.session["user"]
        userdetails = UserData.objects.get(username=request.session["user"])
        reseller = UserData.objects.filter(sponserId=username,postId="User")
        fromsum = balanceTransactionReport.objects.filter(source=userdetails,category='BT').aggregate(Sum('amount'))
        tosum = balanceTransactionReport.objects.filter(destination=userdetails,category='BT').aggregate(Sum('amount'))
        bthist = balanceTransactionReport.objects.filter(source=userdetails).order_by('-date') | balanceTransactionReport.objects.filter(destination=userdetails).order_by('-date')
        return render(request,"sub_reseller/dcard/balanceTransferReport.html",{'form':balancetransferfilterform,'reseller':reseller,'bthist':bthist,'fromsum':fromsum['amount__sum'],'tosum':tosum['amount__sum'],'user':userdetails})
    else:
        return redirect(LoginPage)

def filtersubresellerdcardbtreport(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            form = balancetransferfilterform(request.POST or None)
            print(form.errors)
            if form.is_valid():
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                usertype=form.cleaned_data.get("usertype")
                susername=form.cleaned_data.get("username")
                username = request.session["user"]
                filter={'ffdate':fromdate,'ttdate':todate,'fuser':susername}
                userdetails = UserData.objects.get(username=request.session["user"])
                reseller = UserData.objects.filter(sponserId=username,postId="User")
                fromsum=None
                tosum=None
                bthist=None
                try:
                    if(susername == "Self"):
                        fromsum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails).aggregate(Sum('amount'))
                        tosum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdetails).aggregate(Sum('amount'))
                        bthist = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdetails)
                    elif(susername == "All"):
                        fromsum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails).aggregate(Sum('amount'))
                        tosum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdetails).aggregate(Sum('amount'))
                        bthist = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails)
                    elif(susername != "All"):
                        fromsum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__username=susername).aggregate(Sum('amount'))
                        tosum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdetails).aggregate(Sum('amount'))
                        bthist = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__username=susername)
                except:
                    pass
                return render(request,"sub_reseller/dcard/balanceTransferReport.html",{'form':balancetransferfilterform,'reseller':reseller,'bthist':bthist,'fromsum':fromsum['amount__sum'],'tosum':tosum['amount__sum'],'user':userdetails,'filter':filter})
            else:
                return redirect(subresellerbTReportDcard)
        else:
            return redirect(subresellerbTReportDcard)
    else:
        return redirect(LoginPage)

def subresellerpaymentReportDcard(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        reseller = UserData.objects.filter(sponserId=request.session["user"],postId="User")
        phist = fundTransactionReport.objects.filter(source=userdetails).order_by('-date')|fundTransactionReport.objects.filter(destination=userdetails).order_by('-date')
        bsum = fundTransactionReport.objects.filter(source=userdetails).aggregate(Sum('amount'))
        return render(request,"sub_reseller/dcard/paymentReport.html",{'form':paymentfilterform,'reseller':reseller,'phist':phist,'sum':bsum['amount__sum'],'user':userdetails})
    else:
        return redirect(LoginPage)

def filtersubresellerdcardpaymentreport(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            form = balancetransferfilterform(request.POST or None)
            print(form.errors)
            if form.is_valid():
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                usertype=form.cleaned_data.get("usertype")
                susername=form.cleaned_data.get("username")
                filter={'ffdate':fromdate,'ttdate':todate,'fuser':susername}
                userdetails = UserData.objects.get(username=request.session["user"])
                reseller = UserData.objects.filter(sponserId=username,postId="User")
                bsum=None
                phist=None
                try:
                    if(susername=="Self"):
                        bsum = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails).aggregate(Sum('amount'))
                        phist = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdetails)
                        #print(phist)
                    elif(susername == "All"):
                        bsum = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails).aggregate(Sum('amount'))
                        phist = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails)
                        print(phist)
                    elif(susername != "All"):
                        bsum = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__username=susername).aggregate(Sum('amount'))
                        phist = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__username=susername)
                except Exception as e:
                    print(e)
                    pass
                return render(request,"sub_reseller/dcard/paymentReport.html",{'form':paymentfilterform,'reseller':reseller,'phist':phist,'sum':bsum['amount__sum'],'user':userdetails,'filter':filter})
            else:
                return redirect(subresellerpaymentReportDcard)
        else:
            return redirect(subresellerpaymentReportDcard)
    else:
        return redirect(LoginPage)

def subresellerassignDCardBrands(request):
    if request.session.has_key("user"):
        brands = datacardAssignments.objects.filter(assignedto=request.session["user"]).values('brand','brand__brand','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
        username=request.session["user"]
        bd=list(brands)
        prdcts=list()
        costs=list()
        for i in brands:
            prd=dcardBrands.objects.get(brand=i['brand__brand'])
            #prd=datacardproducts.objects.filter(brand__brand=i['brand__brand'], status=True).order_by('brand').values('brand').annotate(productcount=Count('brand')).values('brand','brand__brand','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
            #print(len(prd))
            if(prd):
                cost=getDatacardProductCost(username,i["brand__brand"])
                data={'cost':cost,'brand':prd.id,'brand__brand':prd.brand,'brand__id':prd.id,'brand__denomination':prd.denomination,'brand__logo':prd.logo.url,'barnd__description':prd.description,'brand__currency':prd.currency}
                prdcts.append(data)
        resellers = UserData.objects.filter(postId="User",sponserId=request.session["user"])
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"sub_reseller/dcard/assignDcardbrand.html",{'brands':bd,'products':prdcts,'resellers':resellers,'user':userdetails})
    else:
        return redirect(LoginPage)

def subresellerdcardstore(request):
    if request.session.has_key("user"):
        username=request.session["user"]
        user = UserData.objects.get(username=username)
        btnlist=list()
        content=list()
        ads = adverisements.objects.filter(adtype="Image",usertype="Sub_Reseller",ctype="Dcard").order_by('-id')[:10]
        dproducts = datacardAssignments.objects.filter(assignedto=username).order_by('brand').values('brand__brand','margin')
        for i in dproducts:
            buttons=(i["brand__brand"]).split(" ")
            if buttons[0] not in btnlist:
                btnlist.append(buttons[0])
        if(len(btnlist)==0):
            pass
        else:
            dcardproducts = datacardAssignments.objects.filter(assignedto=username,brand__brand__contains=btnlist[0]).order_by('brand').values('brand__brand','margin')
            print(dcardproducts)
            #print(buttons)
            for i in dcardproducts:
                dcp=datacardproducts.objects.filter(brand__brand=i["brand__brand"],status=True).order_by('brand').values('brand').annotate(count=Count('brand')).values('count','brand__id','brand__brand','brand__description','brand__denomination','brand__logo','count','brand__currency')
                if(len(dcp)>0):
                    cost=getDatacardProductCost(username,dcp[0]["brand__brand"])
                    data={'brand__id':dcp[0]['brand__id'],'brand__brand':dcp[0]['brand__brand'],'brand__logo':dcp[0]['brand__logo'],'brand__description':dcp[0]['brand__description'],'brand__currency':dcp[0]['brand__currency'],'count':dcp[0]['count'],'cost':cost}
                    content.append(data)
                else:
                    pass
            #print(content)
        return render(request,"sub_reseller/dcard/datastore.html",{'dcardproducts':content,'btnlist':btnlist,'user':user,'ads':ads})
    else:
        return redirect(LoginPage)

def subgetDatacardProductCost(username,brand):
    prdcts=datacardproducts.objects.filter(brand__brand=brand,status=True).order_by('brand').values('brand__denomination')
    prdctcost=0
    margins=0
    while(True):
        userdet = UserData.objects.filter(username=username).values('sponserId','postId')
        pdct = datacardAssignments.objects.filter(assignedto=username, brand__brand=brand).values('margin')
        if(userdet[0]['postId']=="Admin"):
            break;
        else:
            prdctcost = Decimal(prdcts[0]["brand__denomination"])
            prdctcost = prdctcost+Decimal(pdct[0]['margin'])
        username=userdet[0]['sponserId']
    print(prdctcost)
    return prdctcost

def subviewfiltereddatastore(brand):
    brands=datacardproducts.objects.filter(brand__brand__contains=brand,status=True).order_by('brand').values('brand').annotate(productcount=Count('brand')).values('productcount','brand__brand','brand__id','brand__description','brand__denomination','brand__logo','brand__currency')
    return brands

def subresellerfilterdcardstore(request,brand):
    if request.session.has_key("user"):
        #print(brand)
        username = request.session['user']
        user=UserData.objects.get(username=username)
        btnlist=list()
        dproducts = datacardAssignments.objects.filter(assignedto=username).order_by('brand').values('brand__brand','margin')
        ads = adverisements.objects.filter(adtype="Image",usertype="Sub_Reseller",ctype="Dcard").order_by('-id')[:10]
        for j in dproducts:
            buttons=(j["brand__brand"]).split(" ")
            if buttons[0] not in btnlist:
                btnlist.append(buttons[0])
        dcardproducts = datacardAssignments.objects.filter(assignedto=username,brand__brand__contains=brand).order_by('brand').values('brand__brand','margin')
        print(dcardproducts)
        content=list()
        for i in dcardproducts:
            dcp=datacardproducts.objects.filter(brand__brand=i["brand__brand"],status=True).order_by('brand').values('brand').annotate(count=Count('brand')).values('count','brand__id','brand__brand','brand__description','brand__denomination','brand__logo','count','brand__currency')
            if(len(dcp)>0):
                cost=getDatacardProductCost(username,dcp[0]["brand__brand"])
                data={'brand__id':dcp[0]['brand__id'],'brand__brand':dcp[0]['brand__brand'],'brand__logo':dcp[0]['brand__logo'],'brand__description':dcp[0]['brand__description'],'brand__currency':dcp[0]['brand__currency'],'count':dcp[0]['count'],'cost':cost}
                content.append(data)
            else:
                pass
        print(content)
        return render(request,"sub_reseller/dcard/datastore.html",{'dcardproducts':content,'btnlist':btnlist,'user':user,'ads':ads})
    else:
        return redirect(LoginPage)


def subeditresellerProfileDcard(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            user = request.session["user"]
            name = request.POST.get('name', None)
            address = request.POST.get('address', None)
            email = request.POST.get('email', None)
            mobileno = request.POST.get('mobileno', None)
            userDet = UserData.objects.get(username=user)
            userDet.name = name
            userDet.address = address
            userDet.email = email
            userDet.mobileno = mobileno
            userDet.save()
            messages.success(request, 'Successfully Updated')
            return redirect(subresellerprofiledcard)
        else:
            messages.warning(request,'Internal Error Occured')
            return redirect(subresellerprofiledcard)
    else:
        return redirect(LoginPage)


def subresellersubmitUser(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = AddUserDataForm(request.POST or None)
            print(form.errors)
            if form.is_valid():
                username=form.cleaned_data.get("username")
                password=form.cleaned_data.get("password")
                hashkey = username+password
                hash = hashlib.sha256(hashkey.encode()).hexdigest()
                sponser = request.session["user"]
                sponseruser=UserData.objects.get(username=sponser)
                Userdata=form.save(commit=False)
                Userdata.postId="User"
                Userdata.sponserId = sponseruser
                Userdata.status = True
                Userdata.balance = 0
                Userdata.targetAmt = 0
                Userdata.rentalAmt = 0
                Userdata.dcard_status = True
                Userdata.rcard_status = True
                Userdata.password = hash
                Userdata.save()
                messages.success(request, 'Successfully Added')
                return redirect(subreselleraddUserDcard)
            else:
                messages.warning(request, form.errors)
                userdetails = UserData.objects.get(username=request.session["user"])
                form = AddUserDataForm()
                return render(request,"sub_reseller/dcard/addUser.html",{'form':AddUserDataForm,'user':userdetails})
        else:
            userdetails = UserData.objects.get(username=request.session["user"])
            form = AddUserDataForm()
            return render(request,"sub_reseller/dcard/addUser.html",{'form':AddUserDataForm,'user':username})
    else:
        return redirect(LoginPage)

def subresellersubBalTransDcard(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            userType = request.POST.get('userType', None)
            user = request.POST.get('users', None)
            amount = request.POST.get('amount', None)
            userdet = UserData.objects.get(username=user)
            bal = userdet.balance
            newbal=bal+Decimal(amount)
            cdbal = userdet.targetAmt
            newcdbal = cdbal-Decimal(amount)
            userdet.targetAmt = newcdbal
            userdet.balance = newbal
            userdet.save()
            userdetails = UserData.objects.get(username=request.session["user"])
            btreport = balanceTransactionReport()
            btreport.source = userdetails
            btreport.destination = userdet
            btreport.category = "BT"
            btreport.pbalance = bal
            btreport.nbalance = newbal
            btreport.cramount = newcdbal
            btreport.amount = amount
            btreport.remarks = 'Added To Balance'
            btreport.save()
            messages.success(request, 'Successfully Updated The balance')
            return redirect(subresellerbalanceTransferDcard)
            #userdata=UserData.objects.get(username=)
        else:
            messages.warning(request, 'Internal Error Occured')
            return redirect(subresellerbalanceTransferDcard)
    else:
        return redirect(LoginPage)

def subresellersubPayTrans(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            userType = request.POST.get('userType', None)
            user = request.POST.get('users', None)
            amount = request.POST.get('amount', None)
            remarks = request.POST.get('remarks', None)
            userdet = UserData.objects.get(username=user)
            obalance = userdet.targetAmt
            cdbal = userdet.targetAmt
            newcdbal = cdbal+Decimal(amount)
            userdet.targetAmt = newcdbal
            userdet.save()
            closeuser = UserData.objects.get(username=user)
            userdetails = UserData.objects.get(username=request.session["user"])
            ftreport=fundTransactionReport()
            ftreport.source = userdetails
            ftreport.destination = userdet
            ftreport.obalance = obalance
            ftreport.cbalance = closeuser.targetAmt
            ftreport.role = userType
            ftreport.amount = amount
            ftreport.balance = newcdbal
            ftreport.remarks = remarks
            ftreport.save()
            messages.success(request, 'Successfully Updated The balance')
            return redirect(subreselleraddPaymentDcard)
        else:
            messages.warning(request, 'Internal Error Occured')
            return redirect(subreselleraddPaymentDcard)
    else:
        return redirect(LoginPage)

def sub_buy_datacard_brands(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            username=request.session["user"]
            brand = request.POST.get('brandid', None)
            quantity = request.POST.get('quantity', None)
            amt = request.POST.get('amt', None)
            branddet=dcardBrands.objects.get(brand=brand)
            userdet=UserData.objects.get(username=request.session["user"])
            ctime=datetime.now()
            time = timedelta(minutes = 5)
            now_minus_5 = ctime - time
            checkqty=datacardproducts.objects.filter(Q(brand__brand=brand) & Q(status=True) & (Q(sdate__isnull=True) | Q(sdate__lte=now_minus_5))).values('brand').annotate(productcount=Count('brand')).values('productcount')
            print(checkqty)
            needamt=0;
            result=list()
            content=dict()
            licheckqty=list(checkqty)
            brand_id=0
            deno=0
            if(licheckqty[0]['productcount'] >= int(quantity)):
                usertype=''
                marginlist=list()
                margins=0
                count=0;
                flag=True
                prdct_id=''
                mllist=list()
                sponserlist=list()
                prdctdet = datacardproducts.objects.filter(Q(brand__brand=brand) & Q(status=True) & (Q(sdate__isnull=True) | Q(sdate__lte=now_minus_5)))[:int(quantity)]
                ctime = datetime.now()
                for i in prdctdet:
                    i.productstatus=1
                    i.suser = userdet
                    i.sdate = ctime
                    i.save()
                count=0
                admin=''
                while(True):
                    userdet2=UserData.objects.filter(username=username).values('sponserId','postId','balance')
                    margindet=datacardAssignments.objects.filter(assignedto=username,brand__brand=brand).values('margin')
                    if(userdet2[0]['postId']=="Admin"):
                        admin=username
                        break;
                    else:
                        cost=Decimal(amt)
                        prdctcost = (cost*Decimal(quantity))-(Decimal(margins)*Decimal(quantity))
                        margins=margins+Decimal(margindet[0]['margin'])
                        #print(prdctcost)
                        #print(cost)
                        if(userdet2[0]['balance']>=prdctcost):
                            data={'margin':margindet[0]['margin'],'balance':userdet2[0]['balance'],'username':username,'prdctcost':prdctcost}
                            marginlist.append(data)
                            mllist.append(margindet[0]['margin'])
                            sponserlist.append(username)
                        else:
                            flag=False
                            print(flag)
                            break;
                    username=userdet2[0]['sponserId']
                if(flag):
                    try:
                        prdctcddet=datacardproducts.objects.filter(brand__brand=brand,status=True,productstatus=1,suser=userdet,sdate=ctime)[:int(quantity)]
                        for h in prdctcddet:
                            h.status=False
                            h.save()
                            brand_id=h.brand.id
                            deno=h.brand.denomination
                            prdct_id=prdct_id+""+str(h.id)+","
                            res={"productid":h.id,"carduname":h.username,'brand':h.brand.brand,'brand_logo':h.brand.logo.url, 'status':h.status,'suser':username,'sdate':h.sdate}
                            result.append(res)
                        ml=marginlist[::-1]
                        for k in ml:
                            uname = k['username']
                            margin = k['margin']
                            balance = k['balance']
                            pcost = k['prdctcost']
                            cb=Decimal(balance)-Decimal(pcost)
                            userd=UserData.objects.get(username=uname)
                            userd.balance=cb
                            userd.save()
                        mllen = len(mllist)
                        vcrep=vcloudtransactions()
                        vcrep.saleduser = userdet
                        vcrep.brand = brand
                        vcrep.type = "Dcard"
                        vcrep.brand_id = brand_id
                        vcrep.product_id = prdct_id
                        vcrep.quantity = quantity
                        vcrep.amount = amt
                        vcrep.rtype = "Web"
                        vcrep.denominations = deno
                        ms = mllist[::-1]
                        mu = sponserlist[::-1]
                        ad=UserData.objects.get(username=admin)
                        if(mllen==1):
                            vcrep.margin1=ms[0]
                            vcrep.sponser1=ad
                            vcrep.sponser2=UserData.objects.get(username=sponserlist[0])
                        elif(mllen==2):
                            vcrep.margin1=ms[0]
                            vcrep.margin2=ms[1]
                            vcrep.sponser1=ad
                            vcrep.sponser2=UserData.objects.get(username=sponserlist[1])
                            vcrep.sponser3=UserData.objects.get(username=sponserlist[0])
                        else:
                            vcrep.margin1=ms[0]
                            vcrep.margin2=ms[1]
                            vcrep.margin3=ms[2]
                            vcrep.sponser1=ad
                            vcrep.sponser2=UserData.objects.get(username=sponserlist[2])
                            vcrep.sponser3=UserData.objects.get(username=sponserlist[1])
                            vcrep.sponser4=UserData.objects.get(username=sponserlist[0])
                        vcrep.save()
                        obj = vcloudtransactions.objects.latest('id')
                        print(obj.id)
                        content["data"] = result
                        content["res_status"]="success"
                        content["trid"]=obj.id
                    except:
                        content["res_status"]="Failed"
                else:
                    for i in prdctdet:
                        i.suser=None
                        i.save()
                    content["res_status"]="Failed"
            return JsonResponse(content,safe=False)
        else:
            return redirect(subresellerdcardstore)
    else:
        return redirect(LoginPage)

def subresellerdcardviewbrands(request):
    if request.session.has_key("user"):
        if request.session.has_key("user"):
            username = request.session["user"]
            vcdprod=dcardBrands.objects.all()
            resultlist=list()
            statuslist=list()
            for i in vcdprod:
                vca=datacardAssignments.objects.filter(assignedto=username,brand__brand=i.brand)
                if not vca:
                    statuslist.append(False)
                else:
                    statuslist.append(True)
            vcd=list(vcdprod)
            print(vcd)
            print(statuslist)
            #print(data)
            ldb=zip(vcd,statuslist)
            userdetails = UserData.objects.get(username=request.session["user"])
            return render(request,"sub_reseller/dcard/viewBrands.html",{'pdcts':list(ldb),'user':userdetails})
        else:
            return redirect(LoginPage)


#________________RCARD_______________

def subresellerRcardDashboard(request):
    if request.session.has_key("user"):
        last_month = datetime.today() - timedelta(days=1)
        username = request.session["user"]
        #print(last_month)
        reseller = UserData.objects.filter(sponserId=username,postId="User")
        #print(reseller)
        resellerlist=list()
        for i in reseller:
            resellerdata={'username':i.username,'name':i.name}
            resellerlist.append(resellerdata)
        username = request.session["user"]
        type = request.session["usertype"]
        try:
            user = UserData.objects.get(username = username, postId = type)
        except UserData.DoesNotExist:
            return redirect(LoginPage)
        userdetails = UserData.objects.get(username=request.session["user"])
        username=request.session["user"]
        last_month = datetime.today() - timedelta(days=1)
        vcloudtxns = vcloudtransactions.objects.filter(date__gte=last_month,sponser3__username=username,type="Rcard").order_by('-date')
        content=list()
        topuser=list()
        noofrecords=0
        productsum =0
        quantitysum =0
        profitsum =0
        count=0
        for i in vcloudtxns:
            count=count+1
            cost=i.denominations+i.margin1+i.margin2
            productsum=productsum+(cost*i.quantity)
            quantitysum=quantitysum+i.quantity
            if(i.saleduser.username==username):
                profit=0
                #data3={'user':i.sponser2.name,'amount':(i.denominations*i.quantity)}
                data={"id":i.id,"saleduser":i.sponser3.name,"role":i.sponser3.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                content.append(data)
                profitsum = profitsum+profit
            else:
                profit=i.margin3*i.quantity
                data3={'user':i.sponser4.name,'amount':(cost*i.quantity)}
                topuser.append(data3)
                data={"id":i.id,"saleduser":i.sponser4.name,"role":i.sponser4.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                content.append(data)
                profitsum = profitsum+profit
        box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum,'noofrecords':count}
        brand = rcardAssignments.objects.filter(assignedto=username).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description','margin')
        product=list()
        print(brand)
        for i in brand:
            print(i['brand__id'])
            pd=rcardProducts.objects.filter(brand=i['brand__id'],status=True).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
            lpd=list(pd)
            count=0
            if not lpd:
                pass
                #print("Haiii")
            else:
                username=request.session["user"]
                productcost=Decimal(lpd[0]['brand__denomination'])
                print(productcost)
                while(True):
                    userdet2=UserData.objects.filter(username=username).values('sponserId','postId')
                    print(userdet2)
                    margindet=rcardAssignments.objects.filter(assignedto=username,brand__brand=i['brand__brand']).values('margin')
                    if(userdet2[0]['postId']=="Admin"):
                        break;
                    else:
                        print(margindet[0]['margin'])
                        productcost = Decimal(productcost)+Decimal(margindet[0]['margin'])
                        print(productcost)
                        username=userdet2[0]['sponserId']
                    count=int(count)+1
                data={"brand":lpd[0]['brand__brand'],'rate':productcost}
                product.append(data)
                #print(content)
        print(product)
        list3=list()
        sorted_users = sorted(topuser, key=itemgetter('user'))

        for key, group in itertools.groupby(sorted_users, key=lambda x:x['user']):
            amountsum=0
            for g in group:
                amountsum=amountsum+g["amount"]
                #print(amountsum)
            data5={'user':key,'amount':amountsum}
            list3.append(data5)

        return render(request,"sub_reseller/rcard/dashboard-rcard.html",{'filterform':rcardDashboardfilter,'reseller':resellerlist,'recenttransactions':content,'products':product,'user':user,'topuser':list3,'last_month':last_month,'boxval':box_data})
    else:
        return redirect(LoginPage)


def filtersubresellerrcardDashboard(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = rcardDashboardfilter(request.POST or None)
            print(form.errors)
            if form.is_valid():
                currentuser=request.session["user"]
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                usertype=form.cleaned_data.get("usertype")
                uuusername=form.cleaned_data.get("username")
                #mffromdate=datetime.strptime(fromdate, '%b %d %Y %I:%M%p')
                print(type(fromdate))
                print(fromdate.strftime("%B %d, %Y"))
                last_month=fromdate.strftime("%B %d, %I:%M %p")+" To "+todate.strftime("%B %d, %I:%M %p")
                reseller = UserData.objects.filter(sponserId=currentuser,postId="User")
                #print(reseller)
                resellerlist=list()
                for i in reseller:
                    resellerdata={'username':i.username,'name':i.name}
                    resellerlist.append(resellerdata)
                #print(username)
                userdetails = UserData.objects.get(username=request.session["user"])
                vcloudtxns = vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate,sponser3__username=currentuser,type="Rcard",sponser4__username=uuusername).order_by('-date')
                content=list()
                topuser=list()
                noofrecords=0
                productsum =0
                quantitysum =0
                profitsum =0
                count=0
                for i in vcloudtxns:
                    count=count+1
                    cost=i.denominations+i.margin1+i.margin2
                    productsum=productsum+(cost*i.quantity)
                    quantitysum=quantitysum+i.quantity
                    if(i.saleduser.username==username):
                        profit=0
                        #data3={'user':i.sponser2.name,'amount':(i.denominations*i.quantity)}
                        data={"id":i.id,"saleduser":i.sponser3.name,"role":i.sponser3.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                        content.append(data)
                        profitsum = profitsum+profit
                    else:
                        profit=i.margin3*i.quantity
                        data3={'user':i.sponser4.name,'amount':(cost*i.quantity)}
                        topuser.append(data3)
                        data={"id":i.id,"saleduser":i.sponser4.name,"role":i.sponser4.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                        content.append(data)
                        profitsum = profitsum+profit
                box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum,'noofrecords':count}

                brand = rcardAssignments.objects.filter(assignedto=currentuser).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description','margin')
                product=list()
                print(brand)
                for i in brand:
                    print(i['brand__id'])
                    pd=rcardProducts.objects.filter(brand=i['brand__id'],status=True).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
                    lpd=list(pd)
                    count=0
                    if not lpd:
                        pass
                        #print("Haiii")
                    else:
                        username=request.session["user"]
                        productcost=Decimal(lpd[0]['brand__denomination'])
                        print(productcost)
                        while(True):
                            userdet2=UserData.objects.filter(username=username).values('sponserId','postId')
                            print(userdet2)
                            margindet=rcardAssignments.objects.filter(assignedto=username,brand__brand=i['brand__brand']).values('margin')
                            if(userdet2[0]['postId']=="Admin"):
                                break;
                            else:
                                print(margindet[0]['margin'])
                                productcost = Decimal(productcost)+Decimal(margindet[0]['margin'])
                                print(productcost)
                                username=userdet2[0]['sponserId']
                            count=int(count)+1
                        data={"brand":lpd[0]['brand__brand'],'rate':productcost}
                        product.append(data)
                        #print(content)
                print(product)
                list3=list()
                sorted_users = sorted(topuser, key=itemgetter('user'))

                for key, group in itertools.groupby(sorted_users, key=lambda x:x['user']):
                    amountsum=0
                    for g in group:
                        amountsum=amountsum+g["amount"]
                        #print(amountsum)
                    data5={'user':key,'amount':amountsum}
                    list3.append(data5)
                return render(request,"sub_reseller/rcard/dashboard-rcard.html",{'filterform':rcardDashboardfilter,'reseller':resellerlist,'recenttransactions':content,'products':product,'user':userdetails,'topuser':list3,'last_month':last_month,'boxval':box_data})
            else:
                return redirect(subresellerRcardDashboard)
        else:
            return(subresellerRcardDashboard)
    else:
        return redirect(LoginPage)


def subresellerprofilercard(request):
    if request.session.has_key("user"):
        user = request.session["user"]
        userDet = UserData.objects.get(username=user)
        return render(request,"sub_reseller/rcard/editProfile.html",{'user':userDet})
    else:
        return redirect(LoginPage)


def subreselleraddUserRcard(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"sub_reseller/rcard/addUser.html",{'form':AddUserDataForm,'user':userdetails})
    else:
        return redirect(LoginPage)


def subresellerviewUserRcard(request):
    if request.session.has_key("user"):
        user = request.session["user"]
        resellers = UserData.objects.filter(postId="User",sponserId=user)
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"sub_reseller/rcard/viewUser.html",{'resellers':resellers,'user':userdetails})
    else:
        return redirect(LoginPage)

def subresellerbalanceTransferRcard(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        bthist=balanceTransactionReport.objects.filter(source=userdetails,category="BT").order_by('-date')
        #print(bthist)
        return render(request,"sub_reseller/rcard/balanceTransfer.html",{'bthist':bthist,'user':userdetails})
    else:
        return redirect(LoginPage)

def subreselleraddPaymentRcard(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        phist=fundTransactionReport.objects.filter(source=userdetails).order_by('-date')
        return render(request,"sub_reseller/rcard/addPayment.html",{'phist':phist})
    else:
        return redirect(LoginPage)

def subresellerrcardreport(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        username=request.session["user"]
        last_month = datetime.today() - timedelta(days=1)
        vcloudtxns = vcloudtransactions.objects.filter(date__gte=last_month,sponser3__username=username).order_by('-date')
        #vcloudtxns = vcloudtransactions.objects.all().order_by('-date')
        reseller=UserData.objects.filter(sponserId=username,postId="User")
        resellerlist=list()
        vcbrand=vcloudBrands.objects.all()
        vcbrandlist=list()
        for b in vcbrand:
            branddata={'brand':b.brand}
            vcbrandlist.append(branddata)

        for i in reseller:
            resellerdata={'username':i.username,'name':i.name}
            resellerlist.append(resellerdata)
        content=list()
        noofrecords=0
        productsum =0
        quantitysum =0
        profitsum =0
        cost=0
        for i in vcloudtxns:
            cost=i.denominations+i.margin1+i.margin2
            productsum=productsum+(cost*i.quantity)
            quantitysum=quantitysum+i.quantity
            if(i.saleduser.username==username):
                profit=0
                data={"id":i.id,"saleduser":i.sponser3.name,"role":i.sponser3.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                content.append(data)
                profitsum = profitsum+profit
            else:
                profit=(i.margin3*i.quantity)
                data={"id":i.id,"saleduser":i.sponser4.name,"role":i.sponser4.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                content.append(data)
                profitsum = profitsum+profit

        box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum}
        return render(request,"sub_reseller/rcard/rcardreport.html",{'filterform':vcloudreportfilterform,'products':content,'user':userdetails,'reseller':resellerlist, 'brand':vcbrandlist,'box':box_data,'date':last_month})
    else:
        return redirect(LoginPage)

def filtersubresellerrcard_report(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            form = vcloudreportfilterform(request.POST or None)
            print(form.errors)
            if form.is_valid():
                username=request.session["user"]
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                usertype=form.cleaned_data.get("usertype")
                fusername=form.cleaned_data.get("username")
                type=form.cleaned_data.get("type")
                brand=form.cleaned_data.get("brand")
                #print(brand,fusername)
                fuser=''
                if(fusername!='All'):
                    filterdata=UserData.objects.get(username=fusername)
                    fuser=filterdata.name
                else:
                    fuser=fusername
                filter={'ffdate':fromdate,'ttdate':todate,'fuser':fuser}
                userdetails = UserData.objects.get(username=request.session["user"])
                reseller=UserData.objects.filter(sponserId=username,postId="User")
                resellerlist=list()
                vcbrand=vcloudBrands.objects.all()
                vcbrandlist=list()
                for b in vcbrand:
                    branddata={'brand':b.brand}
                    vcbrandlist.append(branddata)

                for i in reseller:
                    resellerdata={'username':i.username,'name':i.name}
                    resellerlist.append(resellerdata)

                content=list()
                noofrecords = 0
                productsum = 0
                quantitysum = 0
                profitsum = 0
                try:
                    print(usertype)
                    print(fusername)
                    print(type)
                    print(brand)
                    if(fusername=="All" and type=="All" and brand=="All"):
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser3__username=username).order_by('-date')
                        print("One")
                    elif(fusername=="All" and type=="All" and brand !="All"):
                        print("TWo")
                        vcloudtxns==vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser3__username=username, brand=brand).order_by('-date')
                    elif(fusername=="All" and type !="All" and brand =="All"):
                        print("Three")
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser3__username=username, type=type).order_by('-date')
                    elif(fusername=="All" and type !="All" and brand !="All"):
                        print("four")
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser3__username=username, brand=brand).order_by('-date')
                    elif(fusername!="All" and type !="All" and brand !="All"):
                        print('five')
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, type=type, sponser3__username=username, sponser4__username=fusername, brand=brand).order_by('-date')
                    elif(fusername =="All" and type =="All" and brand !="All"):
                        print('Six')
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser3__username=username).order_by('-date')
                    elif(fusername =="All" and type =="All" and brand =="All"):
                        print('Six')
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser3__username=username, sponser4__postId=usertype).order_by('-date')
                    elif(fusername !="All" and type =="All" and brand =="All"):
                        print('Six')
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser3__username=username, sponser4__username=fusername).order_by('-date')
                    elif(fusername !="All" and type =="All" and brand =="All"):
                        print('Six')
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser3__username=username, sponser4__username=fusername).order_by('-date')
                    else:
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, sponser3__username=username, sponser4__username=fusername,brand=brand).order_by('-date')
                    print(vcloudtxns)

                    for i in vcloudtxns:
                        cost=i.denominations+i.margin1+i.margin2
                        productsum=productsum+(cost*i.quantity)
                        quantitysum=quantitysum+i.quantity
                        if(i.saleduser.username==username):
                            profit=0
                            data={"id":i.id,"saleduser":i.sponser3.name,"role":i.sponser3.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                            content.append(data)
                            profitsum = profitsum+profit
                        else:
                            profit=(i.margin3*i.quantity)
                            data={"id":i.id,"saleduser":i.sponser4.name,"role":i.sponser4.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit,"rtype":i.rtype}
                            content.append(data)
                            profitsum = profitsum+profit
                except:
                    pass
                box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum}
                return render(request,"sub_reseller/rcard/rcardreport.html",{'filterform':vcloudreportfilterform,'products':content,'user':userdetails,'reseller':resellerlist, 'brand':vcbrandlist,'box':box_data,'filter':filter})
            else:
                return redirect(subresellerrcardreport)
        else:
            return redirect(subresellerrcardreport)
    else:
        return redirect(LoginPage)

def subresellerbTReportRcard(request):
    if request.session.has_key("user"):
        if request.session.has_key("user"):
            username = request.session["user"]
            userdetails = UserData.objects.get(username=request.session["user"])
            reseller = UserData.objects.filter(sponserId=username,postId="User")
            fromsum = balanceTransactionReport.objects.filter(source=userdetails,category='BT').aggregate(Sum('amount'))
            tosum = balanceTransactionReport.objects.filter(destination=userdetails,category='BT').aggregate(Sum('amount'))
            bthist = balanceTransactionReport.objects.filter(source=userdetails).order_by('-date') | balanceTransactionReport.objects.filter(destination=userdetails).order_by('-date')
            return render(request,"sub_reseller/rcard/balanceTransferReport.html",{'form':balancetransferfilterform,'reseller':reseller,'bthist':bthist,'fromsum':fromsum['amount__sum'],'tosum':tosum['amount__sum'],'user':userdetails})
        else:
            return redirect(LoginPage)

def filtersubresellerrcardbtreport(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            form = balancetransferfilterform(request.POST or None)
            print(form.errors)
            if form.is_valid():
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                usertype=form.cleaned_data.get("usertype")
                susername=form.cleaned_data.get("username")
                username = request.session["user"]
                filter={'ffdate':fromdate,'ttdate':todate,'fuser':susername}
                userdetails = UserData.objects.get(username=request.session["user"])
                reseller = UserData.objects.filter(sponserId=username,postId="User")
                fromsum=None
                tosum=None
                bthist=None
                try:
                    if(susername == "Self"):
                        fromsum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails).aggregate(Sum('amount'))
                        tosum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdetails).aggregate(Sum('amount'))
                        bthist = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdetails)
                    elif(susername == "All"):
                        fromsum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails).aggregate(Sum('amount'))
                        tosum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdetails).aggregate(Sum('amount'))
                        bthist = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails)
                    elif(susername != "All"):
                        fromsum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__username=susername).aggregate(Sum('amount'))
                        tosum = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdetails).aggregate(Sum('amount'))
                        bthist = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__username=susername)
                except:
                    pass
                return render(request,"sub_reseller/rcard/balanceTransferReport.html",{'form':balancetransferfilterform,'reseller':reseller,'bthist':bthist,'fromsum':fromsum['amount__sum'],'tosum':tosum['amount__sum'],'user':userdetails,'filter':filter})
            else:
                return redirect(subresellerbTReportRcard)
        else:
            return redirect(subresellerbTReportRcard)
    else:
        return redirect(LoginPage)

def subresellerpaymentReportRcard(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        reseller = UserData.objects.filter(sponserId=request.session["user"],postId="User")
        phist = fundTransactionReport.objects.filter(source=userdetails).order_by('-date')|fundTransactionReport.objects.filter(destination=userdetails).order_by('-date')
        bsum = fundTransactionReport.objects.filter(source=userdetails).aggregate(Sum('amount'))
        return render(request,"sub_reseller/rcard/paymentReport.html",{'form':paymentfilterform,'reseller':reseller,'phist':phist,'sum':bsum['amount__sum'],'user':userdetails})
    else:
        return redirect(LoginPage)

def filtersubresellerrcardpaymentreport(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            form = balancetransferfilterform(request.POST or None)
            print(form.errors)
            if form.is_valid():
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                usertype=form.cleaned_data.get("usertype")
                susername=form.cleaned_data.get("username")
                username = request.session["user"]
                filter={'ffdate':fromdate,'ttdate':todate,'fuser':susername}
                userdetails = UserData.objects.get(username=request.session["user"])
                reseller = UserData.objects.filter(sponserId=username,postId="User")
                bsum=None
                phist=None
                try:
                    if(susername=="Self"):
                        bsum = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails).aggregate(Sum('amount'))
                        phist = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdetails)
                        #print(phist)
                    elif(susername == "All"):
                        bsum = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails).aggregate(Sum('amount'))
                        phist = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails)
                        print(phist)
                    elif(susername != "All"):
                        bsum = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__username=susername).aggregate(Sum('amount'))
                        phist = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails,destination__username=susername)
                except Exception as e:
                    print(e)
                    pass
                return render(request,"sub_reseller/rcard/paymentReport.html",{'form':paymentfilterform,'reseller':reseller,'phist':phist,'sum':bsum['amount__sum'],'user':userdetails,'filter':filter})
            else:
                return redirect(subresellerpaymentReportRcard)
        else:
            return redirect(subresellerpaymentReportRcard)
    else:
        return redirect(LoginPage)

def subresellerassignRCardBrands(request):
    if request.session.has_key("user"):
        brands = rcardAssignments.objects.filter(assignedto=request.session["user"]).values('brand','brand__brand','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
        username=request.session["user"]
        bd=list(brands)
        prdcts=list()
        costs=list()
        for i in brands:
            prd=rcardBrands.objects.get(brand=i['brand__brand'])
            #prd=rcardProducts.objects.filter(brand__brand=i['brand__brand'], status=True).order_by('brand').values('brand').annotate(productcount=Count('brand')).values('brand','brand__brand','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
            if(prd):
                cost=getReachargeProductCost(username,i["brand__brand"])
                data={'cost':cost,'brand':prd.id,'brand__brand':prd.brand,'brand__id':prd.id,'brand__denomination':prd.denomination,'brand__logo':prd.logo.url,'barnd__description':prd.description,'brand__currency':prd.currency}
                prdcts.append(data)

        #print(pddata[0])
        resellers = UserData.objects.filter(postId="User",sponserId=request.session["user"])
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"sub_reseller/rcard/assignRcardbrand.html",{'brands':bd,'products':prdcts,'resellers':resellers,'user':userdetails})
    else:
        return redirect(LoginPage)

def subresellerrcardstore(request):
    if request.session.has_key("user"):
        username=request.session["user"]
        user = UserData.objects.get(username=username)
        ads = adverisements.objects.filter(adtype="Image",usertype="Sub_Reseller",ctype="Rcard").order_by('-id')[:10]
        btnlist=list()
        dproducts = rcardAssignments.objects.filter(assignedto=username).order_by('brand').values('brand__brand','margin')
        for i in dproducts:
            buttons=(i["brand__brand"]).split(" ")
            if buttons[0] not in btnlist:
                btnlist.append(buttons[0])
        content=list()
        if(len(btnlist)!=0):
            dcardproducts = rcardAssignments.objects.filter(assignedto=username,brand__brand__contains=btnlist[0]).order_by('brand').values('brand__brand','margin')
            #print(buttons)
            for i in dcardproducts:
                dcp=rcardProducts.objects.filter(brand__brand=i["brand__brand"],status=True).order_by('brand').values('brand').annotate(count=Count('brand')).values('count','brand__id','brand__brand','brand__description','brand__denomination','brand__logo','count','brand__currency')
                if(len(dcp)>0):
                    cost=getRcardProductCost(username,dcp[0]["brand__brand"])
                    data={'brand__id':dcp[0]['brand__id'],'brand__brand':dcp[0]['brand__brand'],'brand__logo':dcp[0]['brand__logo'],'brand__description':dcp[0]['brand__description'],'brand__currency':dcp[0]['brand__currency'],'count':dcp[0]['count'],'cost':cost}
                    content.append(data)
                    print(content)
                else:
                    pass;
        return render(request,"sub_reseller/rcard/rcardstore.html",{'dcardproducts':content,'btnlist':btnlist,'user':user,'ads':ads})
    else:
        return redirect(LoginPage)

def subgetRcardProductCost(username,brand):
    prdcts=rcardProducts.objects.filter(brand__brand=brand,status=True).order_by('brand').values('brand__denomination')
    prdctcost=0
    margins=0
    while(True):
        userdet = UserData.objects.filter(username=username).values('sponserId','postId')
        pdct = rcardAssignments.objects.filter(assignedto=username, brand__brand=brand).values('margin')
        if(userdet[0]['postId']=="Admin"):
            break;
        else:
            prdctcost = Decimal(prdcts[0]["brand__denomination"])
            prdctcost = prdctcost+Decimal(pdct[0]['margin'])
        username=userdet[0]['sponserId']
    print(prdctcost)
    return prdctcost

def subviewfilteredreachargestore(brand):
    brands=rcardProducts.objects.filter(brand__brand__contains=brand,status=True).order_by('brand').values('brand').annotate(productcount=Count('brand')).values('productcount','brand__brand','brand__id','brand__description','brand__denomination','brand__logo','brand__currency')
    return brands

def subresellerfilterrcardstore(request,brand):
    if request.session.has_key("user"):
        #print(brand)
        username=request.session["user"]
        user = UserData.objects.get(username=username)
        ads = adverisements.objects.filter(adtype="Image",usertype="Sub_Reseller",ctype="Rcard").order_by('-id')[:10]
        btnlist=list()
        dproducts = rcardAssignments.objects.filter(assignedto=username).order_by('brand').values('brand__brand','margin')
        for i in dproducts:
            buttons=(i["brand__brand"]).split(" ")
            if buttons[0] not in btnlist:
                btnlist.append(buttons[0])
        dcardproducts = rcardAssignments.objects.filter(assignedto=username,brand__brand__contains=brand).order_by('brand').values('brand__brand','margin')
        content=list()
        #print(buttons)
        for i in dcardproducts:
            dcp=rcardProducts.objects.filter(brand__brand=i["brand__brand"],status=True).order_by('brand').values('brand').annotate(count=Count('brand')).values('count','brand__id','brand__brand','brand__description','brand__denomination','brand__logo','count','brand__currency')
            if(len(dcp)>0):
                buttons=(dcp[0]["brand__brand"]).split(" ")
                if buttons[0] not in btnlist:
                    btnlist.append(buttons[0])
                cost=getRcardProductCost(username,dcp[0]["brand__brand"])
                data={'brand__id':dcp[0]['brand__id'],'brand__brand':dcp[0]['brand__brand'],'brand__logo':dcp[0]['brand__logo'],'brand__description':dcp[0]['brand__description'],'brand__currency':dcp[0]['brand__currency'],'count':dcp[0]['count'],'cost':cost}
                content.append(data)
                print(content)
            else:
                pass;
        return render(request,"sub_reseller/rcard/rcardstore.html",{'dcardproducts':content,'btnlist':btnlist,'user':user,'ads':ads})
    else:
        return redirect(LoginPage)


def subeditresellerProfileRcard(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            user = request.session["user"]
            name = request.POST.get('name', None)
            address = request.POST.get('address', None)
            email = request.POST.get('email', None)
            mobileno = request.POST.get('mobileno', None)
            userDet = UserData.objects.get(username=user)
            userDet.name = name
            userDet.address = address
            userDet.email = email
            userDet.mobileno = mobileno
            userDet.save()
            messages.success(request, 'Successfully Updated')
            return redirect(subresellerprofilercard)
        else:
            messages.warning(request,'Internal Error Occured')
            return redirect(subresellerprofilercard)
    else:
        return redirect(LoginPage)

def subresellersubmitUser(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = AddUserDataForm(request.POST or None)
            print(form.errors)
            if form.is_valid():
                username=form.cleaned_data.get("username")
                password=form.cleaned_data.get("password")
                hashkey = username+password
                hash = hashlib.sha256(hashkey.encode()).hexdigest()
                sponser = request.session["user"]
                sponseruser=UserData.objects.get(username=sponser)
                Userdata=form.save(commit=False)
                Userdata.postId="User"
                Userdata.sponserId = sponseruser
                Userdata.status = True
                Userdata.balance = 0
                Userdata.targetAmt = 0
                Userdata.rentalAmt = 0
                Userdata.dcard_status = True
                Userdata.rcard_status = True
                Userdata.password = hash
                Userdata.save()
                messages.success(request, 'Successfully Added')
                return redirect(subreselleraddUserRcard)
            else:
                messages.warning(request, form.errors)
                userdetails = UserData.objects.get(username=request.session["user"])
                form = AddUserDataForm()
                return render(request,"sub_reseller/rcard/addUser.html",{'form':AddUserDataForm,'user':userdetails})
        else:
            userdetails = UserData.objects.get(username=request.session["user"])
            form = AddUserDataForm()
            return render(request,"sub_reseller/rcard/addUser.html",{'form':AddUserDataForm,'user':username})
    else:
        return redirect(LoginPage)

def subresellersubBalTransRcard(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            userType = request.POST.get('userType', None)
            user = request.POST.get('users', None)
            amount = request.POST.get('amount', None)
            userdet = UserData.objects.get(username=user)
            bal = userdet.balance
            newbal=bal+Decimal(amount)
            cdbal = userdet.targetAmt
            newcdbal = cdbal-Decimal(amount)
            userdet.targetAmt = newcdbal
            userdet.balance = newbal
            userdet.save()
            userdetails = UserData.objects.get(username=request.session["user"])
            btreport = balanceTransactionReport()
            btreport.source = userdetails
            btreport.destination = userdet
            btreport.category = "BT"
            btreport.pbalance = bal
            btreport.nbalance = newbal
            btreport.cramount = newcdbal
            btreport.amount = amount
            btreport.remarks = 'Added To Balance'
            btreport.save()
            messages.success(request, 'Successfully Updated The balance')
            return redirect(subresellerbalanceTransferRcard)
            #userdata=UserData.objects.get(username=)
        else:
            messages.warning(request, 'Internal Error Occured')
            return redirect(subresellerbalanceTransferRcard)
    else:
        return redirect(LoginPage)

def subresellerrcardsubPayTrans(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            userType = request.POST.get('userType', None)
            user = request.POST.get('users', None)
            amount = request.POST.get('amount', None)
            remarks = request.POST.get('remarks', None)
            userdet = UserData.objects.get(username=user)
            obalance = userdet.targetAmt
            cdbal = userdet.targetAmt
            newcdbal = cdbal+Decimal(amount)
            userdet.targetAmt = newcdbal
            userdet.save()
            closeuser = UserData.objects.get(username=user)
            userdetails = UserData.objects.get(username=request.session["user"])
            ftreport=fundTransactionReport()
            ftreport.source = userdetails
            ftreport.destination = userdet
            ftreport.obalance = obalance
            ftreport.cbalance = closeuser.targetAmt
            ftreport.role = userType
            ftreport.amount = amount
            ftreport.balance = newcdbal
            ftreport.remarks = remarks
            ftreport.save()
            messages.success(request, 'Successfully Updated The balance')
            return redirect(subreselleraddPaymentRcard)
        else:
            messages.warning(request, 'Internal Error Occured')
            return redirect(subreselleraddPaymentRcard)
    else:
        return redirect(LoginPage)

def subresellefilteredrrcardstore(request,brandtype):
    if request.session.has_key("user"):
        username=request.session["user"]
        user = UserData.objects.get(username=username)
        ads = adverisements.objects.filter(adtype="Image",usertype="Sub_Reseller",ctype="Rcard").order_by('-id')[:10]
        btnlist=list()
        dproducts = rcardAssignments.objects.filter(assignedto=username).order_by('brand').values('brand__brand','margin')
        for i in dproducts:
            buttons=(i["brand__brand"]).split(" ")
            if buttons[0] not in btnlist:
                btnlist.append(buttons[0])
        dcardproducts = rcardAssignments.objects.filter(assignedto=username,brand__brand__contains=brandtype).order_by('brand').values('brand__brand','margin')
        content=list()
        #print(buttons)
        for i in dcardproducts:
            dcp=rcardProducts.objects.filter(brand__brand=i["brand__brand"],status=True).order_by('brand').values('brand').annotate(count=Count('brand')).values('count','brand__id','brand__brand','brand__description','brand__denomination','brand__logo','count','brand__currency')
            buttons=(dcp[0]["brand__brand"]).split(" ")
            if buttons[0] not in btnlist:
                btnlist.append(buttons[0])
            cost=getRcardProductCost(username,dcp[0]["brand__brand"])
            data={'brand__id':dcp[0]['brand__id'],'brand__brand':dcp[0]['brand__brand'],'brand__logo':dcp[0]['brand__logo'],'brand__description':dcp[0]['brand__description'],'brand__currency':dcp[0]['brand__currency'],'count':dcp[0]['count'],'cost':cost}
            content.append(data)
            print(content)
        return render(request,"sub_reseller/rcard/rcardstore.html",{'dcardproducts':content,'btnlist':btnlist,'user':user,'ads':ads})
    else:
        return redirect(LoginPage)

def sub_buy_rcard_brands(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            username=request.session["user"]
            brand = request.POST.get('brandid', None)
            quantity = request.POST.get('quantity', None)
            amt = request.POST.get('amt', None)
            branddet=rcardBrands.objects.get(brand=brand)
            userdet=UserData.objects.get(username=request.session["user"])
            ctime=datetime.now()
            time = timedelta(minutes = 5)
            now_minus_5 = ctime - time
            checkqty=rcardProducts.objects.filter(Q(brand__brand=brand) & Q(status=True) & (Q(sdate__isnull=True) | Q(sdate__lte=now_minus_5))).values('brand').annotate(productcount=Count('brand')).values('productcount')
            print(checkqty)
            needamt=0;
            result=list()
            content=dict()
            licheckqty=list(checkqty)
            brand_id=0
            deno=0
            if(licheckqty[0]['productcount'] >= int(quantity)):
                usertype=''
                marginlist=list()
                margins=0
                count=0;
                flag=True
                prdct_id=''
                mllist=list()
                sponserlist=list()
                prdctdet = rcardProducts.objects.filter(Q(brand__brand=brand) & Q(status=True) & (Q(sdate__isnull=True) | Q(sdate__lte=now_minus_5)))[:int(quantity)]
                ctime = datetime.now()
                for i in prdctdet:
                    i.productstatus=1
                    i.suser = userdet
                    i.sdate = ctime
                    i.save()
                count=0
                admin=''
                while(True):
                    userdet2=UserData.objects.filter(username=username).values('sponserId','postId','balance')
                    margindet=rcardAssignments.objects.filter(assignedto=username,brand__brand=brand).values('margin')
                    if(userdet2[0]['postId']=="Admin"):
                        admin=username
                        break;
                    else:
                        cost=Decimal(amt)
                        prdctcost = (cost*Decimal(quantity))-(Decimal(margins)*Decimal(quantity))
                        margins=margins+Decimal(margindet[0]['margin'])
                        #print(prdctcost)
                        #print(cost)
                        if(userdet2[0]['balance']>=prdctcost):
                            data={'margin':margindet[0]['margin'],'balance':userdet2[0]['balance'],'username':username,'prdctcost':prdctcost}
                            marginlist.append(data)
                            mllist.append(margindet[0]['margin'])
                            sponserlist.append(username)
                        else:
                            flag=False
                            print(flag)
                            break;
                    username=userdet2[0]['sponserId']
                if(flag):
                    try:
                        prdctcddet=rcardProducts.objects.filter(brand__brand=brand,status=True,productstatus=1,suser=userdet,sdate=ctime)[:int(quantity)]
                        for h in prdctcddet:
                            h.status=False
                            h.save()
                            brand_id=h.brand.id
                            deno=h.brand.denomination
                            prdct_id=prdct_id+""+str(h.id)+","
                            res={"productid":h.id,"carduname":h.username,'brand':h.brand.brand,'brand_logo':h.brand.logo.url, 'status':h.status,'suser':username,'sdate':h.sdate}
                            result.append(res)
                        ml=marginlist[::-1]
                        for k in ml:
                            uname = k['username']
                            margin = k['margin']
                            balance = k['balance']
                            pcost = k['prdctcost']
                            cb=Decimal(balance)-Decimal(pcost)
                            userd=UserData.objects.get(username=uname)
                            userd.balance=cb
                            userd.save()
                        mllen = len(mllist)
                        vcrep=vcloudtransactions()
                        vcrep.saleduser = userdet
                        vcrep.brand = brand
                        vcrep.type = "Rcard"
                        vcrep.brand_id = brand_id
                        vcrep.product_id = prdct_id
                        vcrep.quantity = quantity
                        vcrep.amount = amt
                        vcrep.rtype = "Web"
                        vcrep.denominations = deno
                        ms = mllist[::-1]
                        mu = sponserlist[::-1]
                        ad=UserData.objects.get(username=admin)
                        if(mllen==1):
                            vcrep.margin1=ms[0]
                            vcrep.sponser1=ad
                            vcrep.sponser2=UserData.objects.get(username=sponserlist[0])
                        elif(mllen==2):
                            vcrep.margin1=ms[0]
                            vcrep.margin2=ms[1]
                            vcrep.sponser1=ad
                            vcrep.sponser2=UserData.objects.get(username=sponserlist[1])
                            vcrep.sponser3=UserData.objects.get(username=sponserlist[0])
                        else:
                            vcrep.margin1=ms[0]
                            vcrep.margin2=ms[1]
                            vcrep.margin3=ms[2]
                            vcrep.sponser1=ad
                            vcrep.sponser2=UserData.objects.get(username=sponserlist[2])
                            vcrep.sponser3=UserData.objects.get(username=sponserlist[1])
                            vcrep.sponser4=UserData.objects.get(username=sponserlist[0])
                        vcrep.save()
                        obj = vcloudtransactions.objects.latest('id')
                        print(obj.id)
                        content["data"] = result
                        content["res_status"]="success"
                        content["trid"]=obj.id
                    except:
                        content["res_status"]="Failed"
                else:
                    for i in prdctdet:
                        i.suser=None
                        i.save()
                    content["res_status"]="Failed"
            return JsonResponse(content,safe=False)
        else:
            return redirect(subresellerrcardstore)
    else:
        return redirect(LoginPage)

def subresellerrcardviewbrands(request):
    if request.session.has_key("user"):
        if request.session.has_key("user"):
            username = request.session["user"]
            vcdprod=rcardBrands.objects.all()
            resultlist=list()
            statuslist=list()
            for i in vcdprod:
                vca=rcardAssignments.objects.filter(assignedto=username,brand__brand=i.brand)
                if not vca:
                    statuslist.append(False)
                else:
                    statuslist.append(True)
            vcd=list(vcdprod)
            print(vcd)
            print(statuslist)
            #print(data)
            ldb=zip(vcd,statuslist)
            userdetails = UserData.objects.get(username=request.session["user"])
            return render(request,"sub_reseller/rcard/viewBrands.html",{'pdcts':list(ldb),'user':userdetails})
        else:
            return redirect(LoginPage)

#________________________________________________________________USER_______________________________________________________________

#________________VCLOUD_______________

def uservcloudhomePage(request):
    if request.session.has_key("user"):
        last_month = datetime.today() - timedelta(days=1)
        username = request.session["user"]
        type = request.session["usertype"]
        userdetails = UserData.objects.get(username=request.session["user"])
        username=request.session["user"]
        vcloudtxns = vcloudtransactions.objects.filter(date__gte=last_month,type="Vcloud",saleduser__username=username).order_by('-date')
        content=list()
        noofrecords=0
        productsum =0
        quantitysum =0
        profitsum =0
        count=0
        for i in vcloudtxns:
            count=count+1
            data={"id":i.id,"saleduser":i.saleduser.name,"role":i.saleduser.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"obalance":i.obalance,"cbalance":i.cbalance,"denomination":i.denominations,"margin":0,"quantity":i.quantity,"amount":(i.amount*i.quantity),"profit":0,"rtype":i.rtype}
            content.append(data)
            productsum=productsum+(i.amount*i.quantity)
            quantitysum=quantitysum+i.quantity
            profitsum = 0
        box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum,'noofrecords':count}
        brand = vcloudAssignments.objects.filter(assignedto=username).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description','margin')
        product=list()
        print(brand)
        for i in brand:
            #print(i['brand__id'])
            pd=vcloudProducts.objects.filter(brand=i['brand__id'],status=True).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
            lpd=list(pd)
            count=0
            if not lpd:
                pass
                #print("Haiii")
            else:
                username=request.session["user"]
                productcost=Decimal(lpd[0]['brand__denomination'])
                print(productcost)
                while(True):
                    userdet2=UserData.objects.filter(username=username).values('sponserId','postId')
                    print(userdet2)
                    margindet=vcloudAssignments.objects.filter(assignedto=username,brand__brand=i['brand__brand']).values('margin')
                    if(userdet2[0]['postId']=="Admin"):
                        break;
                    else:
                        print(margindet[0]['margin'])
                        productcost = Decimal(productcost)+Decimal(margindet[0]['margin'])
                        print(productcost)
                        username=userdet2[0]['sponserId']
                    count=int(count)+1
                data={"brand":lpd[0]['brand__brand'],'rate':productcost}
                product.append(data)
                #print(content)
        print(product)
        return render(request,"user/vcloud/dashboard-vcloud.html",{'filterform':uservclouddashboardfilter,'recenttransactions':content,'products':product,'user':userdetails,'last_month':last_month,'boxval':box_data})
    else:
        return redirect(LoginPage)

def filteruservcloudhomepage(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = uservclouddashboardfilter(request.POST or None)
            print(form.errors)
            if form.is_valid():
                currentuser=request.session["user"]
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                username=request.session["user"]
                #mffromdate=datetime.strptime(fromdate, '%b %d %Y %I:%M%p')
                #print(type(fromdate))
                #print(fromdate.strftime("%B %d, %Y"))
                last_month=fromdate.strftime("%B %d, %I:%M %p")+" To "+todate.strftime("%B %d, %I:%M %p")
                userdetails = UserData.objects.get(username=request.session["user"])
                #vcloudtxns = vcloudtransactions.objects.filter(type="Vcloud").order_by('-date')
                vcloudtxns = vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate,type="Vcloud",saleduser__username=username).order_by('-date')
                content=list()
                noofrecords=0
                productsum =0
                quantitysum =0
                profitsum =0
                count=0
                for i in vcloudtxns:
                    count=count+1
                    data={"id":i.id,"saleduser":i.saleduser.name,"role":i.saleduser.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"obalance":i.obalance,"cbalance":i.cbalance,"denomination":i.denominations,"margin":0,"quantity":i.quantity,"amount":(i.amount*i.quantity),"profit":0,"rtype":i.rtype}
                    content.append(data)
                    productsum=productsum+(i.amount*i.quantity)
                    quantitysum=quantitysum+i.quantity
                    profitsum = 0
                box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum,'noofrecords':count}
                brand=vcloudBrands.objects.all()
                product=list()
                for j in brand:
                    prdcts=vcloudProducts.objects.filter(brand__id=j.id,status=True).order_by("brand__brand").values("brand").annotate(productcount=Count('brand')).values('brand__brand', 'productcount','brand__denomination')
                    #print(prdcts)
                    for k in prdcts:
                        data2={"brand":k['brand__brand'],"count":k['productcount'],"denomination":k['brand__denomination']}
                        product.append(data2)
                #print(topuser)
                return render(request,"user/vcloud/dashboard-vcloud.html",{'filterform':vcloudDashboardfilter,'recenttransactions':content,'products':product,'user':userdetails,'last_month':last_month,'boxval':box_data})
            else:
                return redirect(uservcloudhomePage)
        else:
            return(uservcloudhomePage)
    else:
        return redirect(LoginPage)

def uservcloudprofile(request):
    if request.session.has_key("user"):
        user = request.session["user"]
        userDet = UserData.objects.get(username=user)
        return render(request,"user/vcloud/editProfile.html",{'user':userDet})
    else:
        return redirect(LoginPage)

def userrvcloudreport(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        username=request.session["user"]
        last_month = datetime.today() - timedelta(days=1)
        vcloudtxns = vcloudtransactions.objects.filter(date__gte=last_month,saleduser__username=username).order_by('-date')
        vcbrand=vcloudBrands.objects.all()
        vcbrandlist=list()
        for b in vcbrand:
            branddata={'brand':b.brand}
            vcbrandlist.append(branddata)
        content=list()
        noofrecords=0
        productsum =0
        quantitysum =0
        profitsum =0
        for i in vcloudtxns:
            data={"id":i.id,"saleduser":i.saleduser.name,"role":i.saleduser.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"obalance":i.obalance,"cbalance":i.cbalance,"denomination":i.denominations,"margin":0,"quantity":i.quantity,"amount":(i.amount*i.quantity),"profit":0,"rtype":i.rtype}
            content.append(data)
            productsum=productsum+(i.amount*i.quantity)
            quantitysum=quantitysum+i.quantity
            profitsum = 0
        box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum}
        return render(request,"user/vcloud/vcloudreport.html",{'filterform':uservcloudreportfilterform,'products':content,'user':userdetails,'brand':vcbrandlist,'box':box_data,'date':last_month})
    else:
        return redirect(LoginPage)

def filteruservcloud_report(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            form = uservcloudreportfilterform(request.POST or None)
            print(form.errors)
            if form.is_valid():
                username=request.session["user"]
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                type=form.cleaned_data.get("type")
                brand=form.cleaned_data.get("brand")
                #print(brand,fusername)
                filter={'ffdate':fromdate,'ttdate':todate}
                reseller=UserData.objects.filter(sponserId=username,postId="User")
                resellerlist=list()
                vcbrand=vcloudBrands.objects.all()
                vcbrandlist=list()
                for b in vcbrand:
                    branddata={'brand':b.brand}
                    vcbrandlist.append(branddata)

                userdetails = UserData.objects.get(username=username)
                content=list()
                noofrecords = 0
                productsum = 0
                quantitysum = 0
                profitsum = 0
                vcloudtxns=vcloudtransactions()
                try:
                    print(type)
                    print(brand)
                    if(type=="All" and brand=="All"):
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, saleduser__username=username).order_by('-date')
                        print("One")
                    elif(type=="All" and brand !="All"):
                        print("TWo")
                        vcloudtxns==vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, saleduser__username=username, brand=brand).order_by('-date')
                    elif(type !="All" and brand =="All"):
                        print("Three")
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, saleduser__username=username, type=type).order_by('-date')
                    else:
                        print("four")
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, saleduser__username=username, brand=brand).order_by('-date')
                    print(vcloudtxns)
                    for i in vcloudtxns:
                        data={"id":i.id,"saleduser":i.saleduser.name,"role":i.saleduser.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"obalance":i.obalance,"cbalance":i.cbalance,"denomination":i.denominations,"margin":0,"quantity":i.quantity,"amount":(i.amount*i.quantity),"profit":0,"rtype":i.rtype}
                        content.append(data)
                        productsum=productsum+(i.amount*i.quantity)
                        quantitysum=quantitysum+i.quantity
                        profitsum = profitsum+0
                except:
                    pass
                box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum}
                return render(request,"user/vcloud/vcloudreport.html",{'filterform':uservcloudreportfilterform,'products':content,'user':userdetails, 'brand':vcbrandlist,'box':box_data,'filter':filter})
            else:
                return redirect(userrvcloudreport)
        else:
            return redirect(userrvcloudreport)
    else:
        return redirect(LoginPage)

def uservcloudStore(request):
    if request.session.has_key("user"):
        username=request.session["user"]
        ads = adverisements.objects.filter(adtype="Image",usertype="User",ctype="Vcloud").order_by('-id')[:10]
        pdcts = vcloudAssignments.objects.filter(assignedto=username,brand__category="card with cutting").order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description','margin')
        print(len(list(pdcts)))
        data=dict()
        content = []
        for i in pdcts:
            try:
                print(i['brand__brand'])
                pd=vcloudProducts.objects.filter(brand=i['brand__id'],status=True).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
                lpd=list(pd)
                #print(len(pd))
                count=0
                if not lpd:
                    pass;
                    #print("Haiii")
                else:
                    username=request.session["user"]
                    productcost=Decimal(lpd[0]['brand__denomination'])
                    #print(productcost)
                    while(True):
                        userdet2=UserData.objects.filter(username=username).values('sponserId','postId')
                        #print(userdet2)
                        margindet=vcloudAssignments.objects.filter(assignedto=username,brand__brand=i['brand__brand']).values('margin')
                        print(margindet)
                        if(userdet2[0]['postId']=="Admin"):
                            break;
                        else:
                            productcost = Decimal(productcost)+Decimal(margindet[0]['margin'])
                            #print(productcost)
                            username=userdet2[0]['sponserId']
                        count=int(count)+1
                    data={"brand_id":lpd[0]['brand__id'],"brand__brand":lpd[0]['brand__brand'],'productcount':lpd[0]['productcount'],'brand__logo':lpd[0]['brand__logo'],'brand__denomination':productcost,'brand__currency':lpd[0]['brand__currency'],'brand__description':lpd[0]['brand__description']}
                    content.append(data)
            except Exception as e:
                pass;
        print(content)
        print(len(content))
        buttonlist=["Cutting","Non Cutting"]
        buttonclass=["btn-warning","btn-success"]
        btnlist = zip(buttonlist, buttonclass)
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"user/vcloud/vcloudStore.html",{'pdcts':content,'btnlist':btnlist,'user':userdetails,'ads':ads})
    else:
        return redirect(LoginPage)


def userviewbrands(request):
    if request.session.has_key("user"):
        username = request.session["user"]
        vcdprod=vcloudBrands.objects.all()
        resultlist=list()
        statuslist=list()
        for i in vcdprod:
            vca=vcloudAssignments.objects.filter(assignedto=username,brand__brand=i.brand)
            if not vca:
                statuslist.append(False)
            else:
                statuslist.append(True)
        vcd=list(vcdprod)
        print(vcd)
        print(statuslist)
        #print(data)
        ldb=zip(vcd,statuslist)
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"user/vcloud/viewBrands.html",{'pdcts':list(ldb),'user':userdetails})
    else:
        return redirect(LoginPage)

def uservcloudeditProfile(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            user = request.session["user"]
            name = request.POST.get('name', None)
            address = request.POST.get('address', None)
            email = request.POST.get('email', None)
            mobileno = request.POST.get('mobileno', None)
            userDet = UserData.objects.get(username=user)
            userDet.name = name
            userDet.address = address
            userDet.email = email
            userDet.mobileno = mobileno
            userDet.save()
            messages.success(request, 'Successfully Updated')
            return redirect(uservcloudprofile)
        else:
            messages.warning(request,'Internal Error Occured')
            return redirect(uservcloudprofile)
    else:
        return redirect(LoginPage)

def user_buy_vcloud_brands(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            username=request.session["user"]
            brand = request.POST.get('brandid', None)
            quantity = request.POST.get('quantity', None)
            amt = request.POST.get('amt', None)
            branddet=vcloudBrands.objects.get(brand=brand)
            userdet=UserData.objects.get(username=request.session["user"])
            #checkqty = vcloudProducts.objects.filter(brand__brand=brand, status=True).exclude(productstatus=1).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('productcount')
            ctime=datetime.now()
            time = timedelta(minutes = 5)
            now_minus_5 = ctime - time
            checkqty=vcloudProducts.objects.filter(Q(brand__brand=brand) & Q(status=True) & (Q(sdate__isnull=True) | Q(sdate__lte=now_minus_5))).values('brand').annotate(productcount=Count('brand')).values('productcount')
            print(checkqty)
            needamt=0;
            result=list()
            content=dict()
            licheckqty=list(checkqty)
            brand_id=0
            deno=0
            if(licheckqty[0]['productcount'] >= int(quantity)):
                usertype=''
                marginlist=list()
                margins=0
                count=0;
                flag=True
                prdct_id=''
                mllist=list()
                sponserlist=list()
                prdctdet = vcloudProducts.objects.filter(Q(brand__brand=brand) & Q(status=True) & (Q(sdate__isnull=True) | Q(sdate__lte=now_minus_5)))[:int(quantity)]
                ctime = datetime.now()
                for i in prdctdet:
                    i.productstatus=1
                    i.suser = userdet
                    i.sdate = ctime
                    i.save()
                count=0
                admin=''
                while(True):
                    userdet2=UserData.objects.filter(username=username).values('sponserId','postId','balance')
                    margindet=vcloudAssignments.objects.filter(assignedto=username,brand__brand=brand).values('margin')
                    if(userdet2[0]['postId']=="Admin"):
                        admin=username
                        break;
                    else:
                        cost=Decimal(amt)
                        prdctcost = (cost*Decimal(quantity))-(Decimal(margins)*Decimal(quantity))
                        margins=margins+Decimal(margindet[0]['margin'])
                        #print(prdctcost)
                        #print(cost)
                        if(userdet2[0]['balance']>=prdctcost):
                            data={'margin':margindet[0]['margin'],'balance':userdet2[0]['balance'],'username':username,'prdctcost':prdctcost}
                            marginlist.append(data)
                            mllist.append(margindet[0]['margin'])
                            sponserlist.append(username)
                        else:
                            flag=False
                            print(flag)
                            break;
                    username=userdet2[0]['sponserId']
                if(flag):
                    try:
                        prdctcddet=vcloudProducts.objects.filter(brand__brand=brand,status=True,productstatus=1,suser=userdet,sdate=ctime)[:int(quantity)]
                        for h in prdctcddet:
                            h.status=False
                            h.save()
                            #print(h.username)
                            brand_id=h.brand.id
                            deno=h.brand.denomination
                            prdct_id=prdct_id+""+str(h.id)+","
                            res={"productid":h.id,"carduname":h.username,'brand':h.brand.brand,'brand_logo':h.brand.logo.url,'password':h.password,'status':h.status,'suser':username,'sdate':h.sdate}
                            result.append(res)

                        ml=marginlist[::-1]
                        for k in ml:
                            uname = k['username']
                            margin = k['margin']
                            balance = k['balance']
                            pcost = k['prdctcost']
                            cb=Decimal(balance)-Decimal(pcost)
                            userd=UserData.objects.get(username=uname)
                            userd.balance=cb
                            userd.save()
                        mllen = len(mllist)
                        closeuser=UserData.objects.get(username=request.session["user"])
                        vcrep=vcloudtransactions()
                        vcrep.saleduser = userdet
                        vcrep.brand = brand
                        vcrep.type = "Vcloud"
                        vcrep.brand_id = brand_id
                        vcrep.product_id = prdct_id
                        vcrep.quantity = quantity
                        vcrep.obalance = userdet.balance
                        vcrep.cbalance = closeuser.balance
                        vcrep.amount = amt
                        vcrep.rtype = "Web"
                        vcrep.denominations = deno
                        ms = mllist[::-1]
                        mu = sponserlist[::-1]
                        print(ms)
                        print(admin)
                        ad=UserData.objects.get(username=admin)
                        if(mllen==1):
                            vcrep.margin1=ms[0]
                            vcrep.sponser1=ad
                            vcrep.sponser2=UserData.objects.get(username=sponserlist[0])
                        elif(mllen==2):
                            vcrep.margin1=ms[0]
                            vcrep.margin2=ms[1]
                            vcrep.sponser1=ad
                            vcrep.sponser2=UserData.objects.get(username=sponserlist[1])
                            vcrep.sponser3=UserData.objects.get(username=sponserlist[0])
                        else:
                            vcrep.margin1=ms[0]
                            vcrep.margin2=ms[1]
                            vcrep.margin3=ms[2]
                            vcrep.sponser1=ad
                            vcrep.sponser2=UserData.objects.get(username=sponserlist[2])
                            vcrep.sponser3=UserData.objects.get(username=sponserlist[1])
                            vcrep.sponser4=UserData.objects.get(username=sponserlist[0])
                        vcrep.save()
                        obj = vcloudtransactions.objects.latest('id')
                        print(obj.id)
                        content["data"] = result
                        content["res_status"]="success"
                        content["trid"]=obj.id
                    except:
                        content["res_status"]="Failed"
                else:
                    for i in prdctdet:
                        i.suser=None
                        i.save()
                    content["res_status"]="Failed"
            return JsonResponse(content,safe=False)
        else:
            return redirect(uservcloudStore)
    else:
        return redirect(LoginPage)

def userfilteredvcloudstore(request,brandtype):
    if request.session.has_key("user"):
        username=request.session["user"]
        buttonclass=[]
        ads = adverisements.objects.filter(adtype="Image",usertype="User",ctype="Vcloud").order_by('-id')[:10]
        print(brandtype)
        if(brandtype=="Cutting"):
            pdcts = vcloudAssignments.objects.filter(assignedto=username,brand__category="card with cutting").order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
            data=dict()
            content = []
            for i in pdcts:
                try:
                    print(i['brand__brand'])
                    pd=vcloudProducts.objects.filter(brand=i['brand__id'],status=True).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
                    lpd=list(pd)
                    #print(lpd)
                    #print(productcost)
                    count=0
                    if not lpd:
                        pass;
                        #print("Haiii")
                    else:
                        username=request.session["user"]
                        productcost=Decimal(lpd[0]['brand__denomination'])
                        print(productcost)
                        while(True):
                            userdet2=UserData.objects.filter(username=username).values('sponserId','postId')
                            print(userdet2)
                            margindet=vcloudAssignments.objects.filter(assignedto=username,brand__brand=i['brand__brand']).values('margin')
                            if(userdet2[0]['postId']=="Admin"):
                                break;
                            else:
                                print(margindet[0]['margin'])
                                productcost = Decimal(productcost)+Decimal(margindet[0]['margin'])
                                print(productcost)
                                username=userdet2[0]['sponserId']
                            count=int(count)+1
                        data={"brand_id":lpd[0]['brand__id'],"brand__brand":lpd[0]['brand__brand'],'productcount':lpd[0]['productcount'],'brand__logo':lpd[0]['brand__logo'],'brand__denomination':productcost,'brand__currency':lpd[0]['brand__currency'],'brand__description':lpd[0]['brand__description']}
                        content.append(data)
                        print(content)
                except Exception as e:
                    print(e)
                    pass;
            buttonclass=["btn-warning","btn-success"]
        else:
            pdcts = vcloudAssignments.objects.filter(assignedto=username,brand__category="card without cutting").order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
            print(pdcts)
            data=dict()
            content = []
            for i in pdcts:
                try:
                    print(i['brand__brand'])
                    pd=vcloudProducts.objects.filter(brand=i['brand__id'],status=True).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
                    lpd=list(pd)
                    #print(lpd)
                    #print(productcost)
                    #print(lpd)
                    count=0
                    if not lpd:
                        pass;
                        #print("Haiii")
                    else:
                        username=request.session["user"]
                        productcost=Decimal(lpd[0]['brand__denomination'])
                        #print(productcost)
                        while(True):
                            userdet2=UserData.objects.filter(username=username).values('sponserId','postId')
                            print(userdet2)
                            margindet=vcloudAssignments.objects.filter(assignedto=username,brand__brand=i['brand__brand']).values('margin')
                            #print(margindet)
                            if(userdet2[0]['postId']=="Admin"):
                                break;
                            else:
                                #print(margindet[0]['margin'])
                                productcost = Decimal(productcost)+Decimal(margindet[0]['margin'])
                                #print(productcost)
                                username=userdet2[0]['sponserId']
                            count=int(count)+1
                        data={"brand_id":lpd[0]['brand__id'],"brand__brand":lpd[0]['brand__brand'],'productcount':lpd[0]['productcount'],'brand__logo':lpd[0]['brand__logo'],'brand__denomination':productcost,'brand__currency':lpd[0]['brand__currency'],'brand__description':lpd[0]['brand__description']}
                        content.append(data)
                        #print(content)
                except Exception as e:
                    print(e)
                    pass;
            buttonclass=["btn-success","btn-warning"]
        buttonlist=["Cutting","Non Cutting"]
        btnlist = zip(buttonlist, buttonclass)
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"user/vcloud/vcloudStore.html",{'pdcts':content,'btnlist':btnlist,'user':userdetails,'ads':ads})
    else:
        return redirect(LoginPage)

#________________DCARD_______________

def userDcardDashboard(request):
    if request.session.has_key("user"):
        last_month = datetime.today() - timedelta(days=1)
        #print(last_month)
        userdetails = UserData.objects.get(username=request.session["user"])
        username=request.session["user"]
        vcloudtxns = vcloudtransactions.objects.filter(date__gte=last_month,type="Dcard",saleduser__username=username).order_by('-date')
        content=list()
        noofrecords=0
        productsum =0
        quantitysum =0
        profitsum =0
        count=0
        for i in vcloudtxns:
            count=count+1
            data={"id":i.id,"saleduser":i.saleduser.name,"role":i.saleduser.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"obalance":i.obalance,"cbalance":i.cbalance,"denomination":i.denominations,"margin":0,"quantity":i.quantity,"amount":(i.amount*i.quantity),"profit":0,"rtype":i.rtype}
            content.append(data)
            productsum=productsum+(i.amount*i.quantity)
            quantitysum=quantitysum+i.quantity
            profitsum = 0
        box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum,'noofrecords':count}
        brand = datacardAssignments.objects.filter(assignedto=username).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description','margin')
        product=list()
        for i in brand:
            pd=datacardproducts.objects.filter(brand=i['brand__id'], status=True).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
            lpd=list(pd)
            count=0
            if not lpd:
                pass;
                #break;
                #print("Haiii")
            else:
                username=request.session["user"]
                productcost=Decimal(lpd[0]['brand__denomination'])
                print(productcost)
                while(True):
                    userdet2=UserData.objects.filter(username=username).values('sponserId','postId')
                    print(userdet2)
                    margindet=datacardAssignments.objects.filter(assignedto=username,brand__brand=i['brand__brand']).values('margin')
                    if(userdet2[0]['postId']=="Admin"):
                        break;
                    else:
                        print(margindet[0]['margin'])
                        productcost = Decimal(productcost)+Decimal(margindet[0]['margin'])
                        print(productcost)
                        username=userdet2[0]['sponserId']
                    count=int(count)+1
                data={"brand":lpd[0]['brand__brand'],'rate':productcost}
                product.append(data)

        return render(request,"user/dcard/dashboard-dcard.html",{'filterform':userdcardDashboardfilter,'recenttransactions':content,'products':product,'user':userdetails,'last_month':last_month,'boxval':box_data})
    else:
        return redirect(LoginPage)

def filteruserDcardDashboard(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = userdcardDashboardfilter(request.POST or None)
            print("Haiii")
            print(form.errors)
            if form.is_valid():
                currentuser=request.session["user"]
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                #mffromdate=datetime.strptime(fromdate, '%b %d %Y %I:%M%p')
                #print(type(fromdate))
                print(fromdate.strftime("%B %d, %Y"))
                last_month=fromdate.strftime("%B %d, %I:%M %p")+" To "+todate.strftime("%B %d, %I:%M %p")

                userdetails = UserData.objects.get(username=request.session["user"])
                vcloudtxns = vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate,type="Dcard",saleduser__username=currentuser).order_by('-date')
                content=list()
                noofrecords=0
                productsum =0
                quantitysum =0
                profitsum =0
                count=0
                for i in vcloudtxns:
                    count=count+1
                    data={"id":i.id,"saleduser":i.saleduser.name,"role":i.saleduser.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"obalance":i.obalance,"cbalance":i.cbalance,"denomination":i.denominations,"margin":0,"quantity":i.quantity,"amount":(i.amount*i.quantity),"profit":0,"rtype":i.rtype}
                    content.append(data)
                    productsum=productsum+(i.amount*i.quantity)
                    quantitysum=quantitysum+i.quantity
                    profitsum = 0
                box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum,'noofrecords':count}
                brand = datacardAssignments.objects.filter(assignedto=currentuser).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description','margin')
                product=list()
                print(brand)
                for i in brand:
                    print(i['brand__id'])
                    pd=datacardproducts.objects.filter(brand=i['brand__id'],status=True).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
                    lpd=list(pd)
                    count=0
                    if not lpd:
                        pass
                        #print("Haiii")
                    else:
                        username=request.session["user"]
                        productcost=Decimal(lpd[0]['brand__denomination'])
                        print(productcost)
                        while(True):
                            userdet2=UserData.objects.filter(username=username).values('sponserId','postId')
                            print(userdet2)
                            margindet=datacardAssignments.objects.filter(assignedto=username,brand__brand=i['brand__brand']).values('margin')
                            if(userdet2[0]['postId']=="Admin"):
                                break;
                            else:
                                print(margindet[0]['margin'])
                                productcost = Decimal(productcost)+Decimal(margindet[0]['margin'])
                                print(productcost)
                                username=userdet2[0]['sponserId']
                            count=int(count)+1
                        data={"brand":lpd[0]['brand__brand'],'rate':productcost}
                        product.append(data)
                        #print(content)
                #print(product)
                return render(request,"user/dcard/dashboard-dcard.html",{'filterform':userdcardDashboardfilter,'recenttransactions':content,'products':product,'user':userdetails,'last_month':last_month,'boxval':box_data})
            else:
                return redirect(userDcardDashboard)
        else:
            return redirect(userDcardDashboard)
    else:
        return redirect(LoginPage)

def userprofiledcard(request):
    if request.session.has_key("user"):
        user = request.session["user"]
        userDet = UserData.objects.get(username=user)
        return render(request,"user/dcard/editProfile.html",{'user':userDet})
    else:
        return redirect(LoginPage)

def userdatacardreport(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        username=request.session["user"]
        last_month = datetime.today() - timedelta(days=1)
        vcloudtxns = vcloudtransactions.objects.filter(date__gte=last_month,saleduser__username=username).order_by('-date')
        vcbrand=vcloudBrands.objects.all()
        vcbrandlist=list()
        for b in vcbrand:
            branddata={'brand':b.brand}
            vcbrandlist.append(branddata)
        content=list()
        noofrecords=0
        productsum =0
        quantitysum =0
        profitsum =0
        for i in vcloudtxns:
            data={"id":i.id,"saleduser":i.saleduser.name,"role":i.saleduser.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"obalance":i.obalance,"cbalance":i.cbalance,"denomination":i.denominations,"margin":0,"quantity":i.quantity,"amount":(i.amount*i.quantity),"profit":0,"rtype":i.rtype}
            content.append(data)
            productsum=productsum+(i.amount*i.quantity)
            quantitysum=quantitysum+i.quantity
            profitsum = 0
        box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum}
        return render(request,"user/dcard/dcardreport.html",{'filterform':uservcloudreportfilterform,'products':content,'user':userdetails,'brand':vcbrandlist,'box':box_data,'date':last_month})
    else:
        return redirect(LoginPage)

def filteruserdcard_report(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            form = uservcloudreportfilterform(request.POST or None)
            print(form.errors)
            if form.is_valid():
                username=request.session["user"]
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                type=form.cleaned_data.get("type")
                brand=form.cleaned_data.get("brand")
                #print(brand,fusername)
                filter={'ffdate':fromdate,'ttdate':todate}
                vcbrand=vcloudBrands.objects.all()
                vcbrandlist=list()
                for b in vcbrand:
                    branddata={'brand':b.brand}
                    vcbrandlist.append(branddata)
                userdetails = UserData.objects.get(username=username)
                content=list()
                noofrecords=0
                productsum =0
                quantitysum =0
                profitsum =0
                vcloudtxns=vcloudtransactions()
                try:
                    print(type)
                    print(brand)
                    if(type=="All" and brand=="All"):
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, saleduser__username=username).order_by('-date')
                        print("One")
                    elif(type=="All" and brand !="All"):
                        print("TWo")
                        vcloudtxns==vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, saleduser__username=username, brand=brand).order_by('-date')
                    elif(type !="All" and brand =="All"):
                        print("Three")
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, saleduser__username=username, type=type).order_by('-date')
                    else:
                        print("four")
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, saleduser__username=username, brand=brand).order_by('-date')
                    print(vcloudtxns)
                    for i in vcloudtxns:
                        data={"id":i.id,"saleduser":i.saleduser.name,"role":i.saleduser.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"obalance":i.obalance,"cbalance":i.cbalance,"denomination":i.denominations,"margin":0,"quantity":i.quantity,"amount":(i.amount*i.quantity),"profit":0,"rtype":i.rtype}
                        content.append(data)
                        productsum=productsum+(i.amount*i.quantity)
                        quantitysum=quantitysum+i.quantity
                        profitsum = profitsum+0
                except:
                    pass
                box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum}
                return render(request,"user/dcard/dcardreport.html",{'filterform':uservcloudreportfilterform,'products':content,'user':userdetails, 'brand':vcbrandlist,'box':box_data,'filter':filter})
            else:
                return redirect(userdatacardreport)
        else:
            return redirect(userdatacardreport)
    else:
        return redirect(LoginPage)

def userdcardstore(request):
    if request.session.has_key("user"):
        username=request.session["user"]
        user = UserData.objects.get(username=username)
        btnlist=list()
        content=list()
        ads = adverisements.objects.filter(adtype="Image",usertype="User",ctype="Dcard").order_by('-id')[:10]
        dproducts = datacardAssignments.objects.filter(assignedto=username).order_by('brand').values('brand__brand','margin')
        for i in dproducts:
            buttons=(i["brand__brand"]).split(" ")
            if buttons[0] not in btnlist:
                btnlist.append(buttons[0])
        if(len(btnlist)==0):
            pass
        else:
            dcardproducts = datacardAssignments.objects.filter(assignedto=username,brand__brand__contains=btnlist[0]).order_by('brand').values('brand__brand','margin')
            print(dcardproducts)
            #print(buttons)
            for i in dcardproducts:
                dcp=datacardproducts.objects.filter(brand__brand=i["brand__brand"],status=True).order_by('brand').values('brand').annotate(count=Count('brand')).values('count','brand__id','brand__brand','brand__description','brand__denomination','brand__logo','count','brand__currency')
                if(len(dcp)>0):
                    cost=getDatacardProductCost(username,dcp[0]["brand__brand"])
                    data={'brand__id':dcp[0]['brand__id'],'brand__brand':dcp[0]['brand__brand'],'brand__logo':dcp[0]['brand__logo'],'brand__description':dcp[0]['brand__description'],'brand__currency':dcp[0]['brand__currency'],'count':dcp[0]['count'],'cost':cost}
                    content.append(data)
                else:
                    pass
        return render(request,"user/dcard/datastore.html",{'dcardproducts':content,'btnlist':btnlist,'user':user,'ads':ads})
    else:
        return redirect(LoginPage)

def userfilterdcardstore(request,brandtype):
    if request.session.has_key("user"):
        #print(brand)
        username = request.session['user']
        user=UserData.objects.get(username=username)
        btnlist=list()
        ads = adverisements.objects.filter(adtype="Image",usertype="User",ctype="Dcard").order_by('-id')[:10]
        dproducts = datacardAssignments.objects.filter(assignedto=username).order_by('brand').values('brand__brand','margin')
        for j in dproducts:
            buttons=(j["brand__brand"]).split(" ")
            if buttons[0] not in btnlist:
                btnlist.append(buttons[0])
        dcardproducts = datacardAssignments.objects.filter(assignedto=username,brand__brand__contains=brandtype).order_by('brand').values('brand__brand','margin')
        print(dcardproducts)
        content=list()
        for i in dcardproducts:
            dcp=datacardproducts.objects.filter(brand__brand=i["brand__brand"],status=True).order_by('brand').values('brand').annotate(count=Count('brand')).values('count','brand__id','brand__brand','brand__description','brand__denomination','brand__logo','count','brand__currency')
            if(len(dcp)>0):
                cost=getDatacardProductCost(username,dcp[0]["brand__brand"])
                data={'brand__id':dcp[0]['brand__id'],'brand__brand':dcp[0]['brand__brand'],'brand__logo':dcp[0]['brand__logo'],'brand__description':dcp[0]['brand__description'],'brand__currency':dcp[0]['brand__currency'],'count':dcp[0]['count'],'cost':cost}
                content.append(data)
            else:
                pass;
        print(content)
        return render(request,"user/dcard/datastore.html",{'dcardproducts':content,'btnlist':btnlist,'user':user,'ads':ads})
    else:
        return redirect(LoginPage)


def usereditProfileDcard(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            user = request.session["user"]
            name = request.POST.get('name', None)
            address = request.POST.get('address', None)
            email = request.POST.get('email', None)
            mobileno = request.POST.get('mobileno', None)
            userDet = UserData.objects.get(username=user)
            userDet.name = name
            userDet.address = address
            userDet.email = email
            userDet.mobileno = mobileno
            userDet.save()
            messages.success(request, 'Successfully Updated')
            return redirect(userprofiledcard)
        else:
            messages.warning(request,'Internal Error Occured')
            return redirect(userprofiledcard)
    else:
        return redirect(LoginPage)

def user_buy_datacard_brands(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            username=request.session["user"]
            brand = request.POST.get('brandid', None)
            quantity = request.POST.get('quantity', None)
            amt = request.POST.get('amt', None)
            branddet=dcardBrands.objects.get(brand=brand)
            userdet=UserData.objects.get(username=request.session["user"])
            ctime=datetime.now()
            time = timedelta(minutes = 5)
            now_minus_5 = ctime - time
            checkqty=datacardproducts.objects.filter(Q(brand__brand=brand) & Q(status=True) & (Q(sdate__isnull=True) | Q(sdate__lte=now_minus_5))).values('brand').annotate(productcount=Count('brand')).values('productcount')
            print(checkqty)
            needamt=0;
            result=list()
            content=dict()
            licheckqty=list(checkqty)
            brand_id=0
            deno=0
            if(licheckqty[0]['productcount'] >= int(quantity)):
                usertype=''
                marginlist=list()
                margins=0
                count=0;
                flag=True
                prdct_id=''
                mllist=list()
                sponserlist=list()
                prdctdet = datacardproducts.objects.filter(Q(brand__brand=brand) & Q(status=True) & (Q(sdate__isnull=True) | Q(sdate__lte=now_minus_5)))[:int(quantity)]
                ctime = datetime.now()
                for i in prdctdet:
                    i.productstatus=1
                    i.suser = userdet
                    i.sdate = ctime
                    i.save()
                count=0
                admin=''
                while(True):
                    userdet2=UserData.objects.filter(username=username).values('sponserId','postId','balance')
                    margindet=datacardAssignments.objects.filter(assignedto=username,brand__brand=brand).values('margin')
                    if(userdet2[0]['postId']=="Admin"):
                        admin=username
                        break;
                    else:
                        cost=Decimal(amt)
                        prdctcost = (cost*Decimal(quantity))-(Decimal(margins)*Decimal(quantity))
                        margins=margins+Decimal(margindet[0]['margin'])
                        #print(prdctcost)
                        #print(cost)
                        if(userdet2[0]['balance']>=prdctcost):
                            data={'margin':margindet[0]['margin'],'balance':userdet2[0]['balance'],'username':username,'prdctcost':prdctcost}
                            marginlist.append(data)
                            mllist.append(margindet[0]['margin'])
                            sponserlist.append(username)
                        else:
                            flag=False
                            print(flag)
                            break;
                    username=userdet2[0]['sponserId']
                if(flag):
                    try:
                        prdctcddet=datacardproducts.objects.filter(brand__brand=brand,status=True,productstatus=1,suser=userdet,sdate=ctime)[:int(quantity)]
                        for h in prdctcddet:
                            h.status=False
                            h.save()
                            brand_id=h.brand.id
                            deno=h.brand.denomination
                            prdct_id=prdct_id+""+str(h.id)+","
                            res={"productid":h.id,"carduname":h.username,'brand':h.brand.brand,'brand_logo':h.brand.logo.url, 'status':h.status,'suser':username,'sdate':h.sdate}
                            result.append(res)
                        ml=marginlist[::-1]
                        for k in ml:
                            uname = k['username']
                            margin = k['margin']
                            balance = k['balance']
                            pcost = k['prdctcost']
                            cb=Decimal(balance)-Decimal(pcost)
                            userd=UserData.objects.get(username=uname)
                            userd.balance=cb
                            userd.save()
                        mllen = len(mllist)
                        closeuser=UserData.objects.get(username=request.session["user"])
                        vcrep=vcloudtransactions()
                        vcrep.saleduser = userdet
                        vcrep.brand = brand
                        vcrep.type = "Dcard"
                        vcrep.brand_id = brand_id
                        vcrep.product_id = prdct_id
                        vcrep.quantity = quantity
                        vcrep.obalance = userdet.balance
                        vcrep.cbalance = closeuser.balance
                        vcrep.amount = amt
                        vcrep.rtype = "Web"
                        vcrep.denominations = deno
                        ms = mllist[::-1]
                        mu = sponserlist[::-1]
                        ad=UserData.objects.get(username=admin)
                        if(mllen==1):
                            vcrep.margin1=ms[0]
                            vcrep.sponser1=ad
                            vcrep.sponser2=UserData.objects.get(username=sponserlist[0])
                        elif(mllen==2):
                            vcrep.margin1=ms[0]
                            vcrep.margin2=ms[1]
                            vcrep.sponser1=ad
                            vcrep.sponser2=UserData.objects.get(username=sponserlist[1])
                            vcrep.sponser3=UserData.objects.get(username=sponserlist[0])
                        else:
                            vcrep.margin1=ms[0]
                            vcrep.margin2=ms[1]
                            vcrep.margin3=ms[2]
                            vcrep.sponser1=ad
                            vcrep.sponser2=UserData.objects.get(username=sponserlist[2])
                            vcrep.sponser3=UserData.objects.get(username=sponserlist[1])
                            vcrep.sponser4=UserData.objects.get(username=sponserlist[0])
                        vcrep.save()
                        obj = vcloudtransactions.objects.latest('id')
                        print(obj.id)
                        content["data"] = result
                        content["res_status"]="success"
                        content["trid"]=obj.id
                    except:
                        content["res_status"]="Failed"
                else:
                    for i in prdctdet:
                        i.suser=None
                        i.save()
                    content["res_status"]="Failed"
            return JsonResponse(content,safe=False)
        else:
            return redirect(userdcardstore)
    else:
        return redirect(LoginPage)

def userdcardviewbrands(request):
    if request.session.has_key("user"):
        username = request.session["user"]
        vcdprod=dcardBrands.objects.all()
        resultlist=list()
        statuslist=list()
        for i in vcdprod:
            vca=datacardAssignments.objects.filter(assignedto=username,brand__brand=i.brand)
            if not vca:
                statuslist.append(False)
            else:
                statuslist.append(True)
        vcd=list(vcdprod)
        print(vcd)
        print(statuslist)
        #print(data)
        ldb=zip(vcd,statuslist)
        userdetails = UserData.objects.get(username=request.session["user"])
        return render(request,"user/dcard/viewBrands.html",{'pdcts':list(ldb),'user':userdetails})
    else:
        return redirect(LoginPage)

#________________RCARD_______________

def userRcardDashboard(request):
    if request.session.has_key("user"):
        last_month = datetime.today() - timedelta(days=1)

        username = request.session["user"]
        type = request.session["usertype"]
        try:
            user = UserData.objects.get(username = username, postId = type)
        except UserData.DoesNotExist:
            return redirect(LoginPage)
        userdetails = UserData.objects.get(username=request.session["user"])
        username=request.session["user"]
        vcloudtxns = vcloudtransactions.objects.filter(date__gte=last_month,type="Rcard",saleduser__username=username).order_by('-date')
        content=list()
        noofrecords=0
        productsum =0
        quantitysum =0
        profitsum =0
        count=0
        for i in vcloudtxns:
            count=count+1
            data={"id":i.id,"saleduser":i.saleduser.name,"role":i.saleduser.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"obalance":i.obalance,"cbalance":i.cbalance,"denomination":i.denominations,"margin":0,"quantity":i.quantity,"amount":(i.amount*i.quantity),"profit":0,"rtype":i.rtype}
            content.append(data)
            productsum=productsum+(i.amount*i.quantity)
            quantitysum=quantitysum+i.quantity
            profitsum = 0
        box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum,'noofrecords':count}
        brand = rcardAssignments.objects.filter(assignedto=username).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description','margin')
        product=list()
        print(brand)
        for i in brand:
            print(i['brand__id'])
            pd=rcardProducts.objects.filter(brand=i['brand__id'],status=True).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
            lpd=list(pd)
            count=0
            if not lpd:
                pass
                #print("Haiii")
            else:
                username=request.session["user"]
                productcost=Decimal(lpd[0]['brand__denomination'])
                print(productcost)
                while(True):
                    userdet2=UserData.objects.filter(username=username).values('sponserId','postId')
                    print(userdet2)
                    margindet=rcardAssignments.objects.filter(assignedto=username,brand__brand=i['brand__brand']).values('margin')
                    if(userdet2[0]['postId']=="Admin"):
                        break;
                    else:
                        print(margindet[0]['margin'])
                        productcost = Decimal(productcost)+Decimal(margindet[0]['margin'])
                        print(productcost)
                        username=userdet2[0]['sponserId']
                    count=int(count)+1
                data={"brand":lpd[0]['brand__brand'],'rate':productcost}
                product.append(data)
                #print(content)
        print(product)

        return render(request,"user/rcard/dashboard-rcard.html",{'filterform':userrcardDashboardfilter,'recenttransactions':content,'products':product,'user':user,'last_month':last_month,'boxval':box_data})
    else:
        return redirect(LoginPage)

def filteruserrcardDashboard(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = userrcardDashboardfilter(request.POST or None)
            print("Haiii")
            print(form.errors)
            if form.is_valid():
                currentuser=request.session["user"]
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                #mffromdate=datetime.strptime(fromdate, '%b %d %Y %I:%M%p')
                #print(type(fromdate))
                print(fromdate.strftime("%B %d, %Y"))
                last_month=fromdate.strftime("%B %d, %I:%M %p")+" To "+todate.strftime("%B %d, %I:%M %p")
                userdetails = UserData.objects.get(username=request.session["user"])
                vcloudtxns = vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate,type="Rcard",saleduser__username=currentuser).order_by('-date')
                content=list()
                noofrecords=0
                productsum =0
                quantitysum =0
                profitsum =0
                count=0
                for i in vcloudtxns:
                    count=count+1
                    data={"id":i.id,"saleduser":i.saleduser.name,"role":i.saleduser.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"obalance":i.obalance,"cbalance":i.cbalance,"denomination":i.denominations,"margin":0,"quantity":i.quantity,"amount":(i.amount*i.quantity),"profit":0,"rtype":i.rtype}
                    content.append(data)
                    productsum=productsum+(i.amount*i.quantity)
                    quantitysum=quantitysum+i.quantity
                    profitsum = 0
                box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum,'noofrecords':count}
                brand = rcardAssignments.objects.filter(assignedto=currentuser).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description','margin')
                product=list()
                print(brand)
                for i in brand:
                    print(i['brand__id'])
                    pd=rcardProducts.objects.filter(brand=i['brand__id'],status=True).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
                    lpd=list(pd)
                    count=0
                    if not lpd:
                        pass
                        #print("Haiii")
                    else:
                        username=request.session["user"]
                        productcost=Decimal(lpd[0]['brand__denomination'])
                        print(productcost)
                        while(True):
                            userdet2=UserData.objects.filter(username=username).values('sponserId','postId')
                            print(userdet2)
                            margindet=rcardAssignments.objects.filter(assignedto=username,brand__brand=i['brand__brand']).values('margin')
                            if(userdet2[0]['postId']=="Admin"):
                                break;
                            else:
                                print(margindet[0]['margin'])
                                productcost = Decimal(productcost)+Decimal(margindet[0]['margin'])
                                print(productcost)
                                username=userdet2[0]['sponserId']
                            count=int(count)+1
                        data={"brand":lpd[0]['brand__brand'],'rate':productcost}
                        product.append(data)
                        #print(content)
                #print(product)
                return render(request,"user/rcard/dashboard-rcard.html",{'filterform':userrcardDashboardfilter,'recenttransactions':content,'products':product,'user':userdetails,'last_month':last_month,'boxval':box_data})
            else:
                return redirect(userRcardDashboard)
        else:
            return redirect(userRcardDashboard)
    else:
        return redirect(LoginPage)

def userprofileRcard(request):
    if request.session.has_key("user"):
        user = request.session["user"]
        userDet = UserData.objects.get(username=user)
        return render(request,"user/rcard/editProfile.html",{'user':userDet})
    else:
        return redirect(LoginPage)

def userrcardreport(request):
    if request.session.has_key("user"):
        userdetails = UserData.objects.get(username=request.session["user"])
        username=request.session["user"]
        last_month = datetime.today() - timedelta(days=1)
        vcloudtxns = vcloudtransactions.objects.filter(date__gte=last_month,saleduser__username=username).order_by('-date')
        vcbrand=vcloudBrands.objects.all()
        vcbrandlist=list()
        for b in vcbrand:
            branddata={'brand':b.brand}
            vcbrandlist.append(branddata)
        content=list()
        noofrecords=0
        productsum =0
        quantitysum =0
        profitsum =0
        for i in vcloudtxns:
            data={"id":i.id,"saleduser":i.saleduser.name,"role":i.saleduser.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"obalance":i.obalance,"cbalance":i.cbalance,"denomination":i.denominations,"margin":0,"quantity":i.quantity,"amount":(i.amount*i.quantity),"profit":0,"rtype":i.rtype}
            content.append(data)
            productsum=productsum+(i.amount*i.quantity)
            quantitysum=quantitysum+i.quantity
            profitsum = 0
        box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum}
        return render(request,"user/rcard/rcardreport.html",{'filterform':uservcloudreportfilterform,'products':content,'user':userdetails,'brand':vcbrandlist,'box':box_data,'date':last_month})
    else:
        return redirect(LoginPage)

def filteruserrcard_report(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            form = uservcloudreportfilterform(request.POST or None)
            print(form.errors)
            if form.is_valid():
                username=request.session["user"]
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                type=form.cleaned_data.get("type")
                brand=form.cleaned_data.get("brand")
                #print(brand,fusername)
                filter={'ffdate':fromdate,'ttdate':todate}
                vcbrand=vcloudBrands.objects.all()
                vcbrandlist=list()
                for b in vcbrand:
                    branddata={'brand':b.brand}
                    vcbrandlist.append(branddata)

                userdetails = UserData.objects.get(username=username)
                content=list()
                noofrecords = 0
                productsum = 0
                quantitysum = 0
                profitsum = 0
                vcloudtxns=vcloudtransactions()
                try:
                    print(type)
                    print(brand)
                    if(type=="All" and brand=="All"):
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, saleduser__username=username).order_by('-date')
                        print("One")
                    elif(type=="All" and brand !="All"):
                        print("TWo")
                        vcloudtxns==vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, saleduser__username=username, brand=brand).order_by('-date')
                    elif(type !="All" and brand =="All"):
                        print("Three")
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, saleduser__username=username, type=type).order_by('-date')
                    else:
                        print("four")
                        vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate, saleduser__username=username, brand=brand).order_by('-date')
                    print(vcloudtxns)
                    for i in vcloudtxns:
                        data={"id":i.id,"saleduser":i.saleduser.name,"role":i.saleduser.postId,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"quantity":i.quantity,"amount":(i.amount*i.quantity),"profit":0,"rtype":i.rtype}
                        content.append(data)
                        productsum=productsum+(i.amount*i.quantity)
                        quantitysum=quantitysum+i.quantity
                        profitsum = profitsum+0
                except:
                    pass
                box_data={'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum}
                return render(request,"user/rcard/rcardreport.html",{'filterform':uservcloudreportfilterform,'products':content,'user':userdetails, 'brand':vcbrandlist,'box':box_data,'filter':filter})
            else:
                return redirect(userdatacardreport)
        else:
            return redirect(userdatacardreport)
    else:
        return redirect(LoginPage)

def userrcardstore(request):
    if request.session.has_key("user"):
        username=request.session["user"]
        user = UserData.objects.get(username=username)
        ads = adverisements.objects.filter(adtype="Image",usertype="User",ctype="Rcard").order_by('-id')[:10]
        btnlist=list()
        dproducts = rcardAssignments.objects.filter(assignedto=username).order_by('brand').values('brand__brand','margin')
        for i in dproducts:
            buttons=(i["brand__brand"]).split(" ")
            if buttons[0] not in btnlist:
                btnlist.append(buttons[0])
        content=list()
        if(len(btnlist)==0):
            pass
        else:
            dcardproducts = rcardAssignments.objects.filter(assignedto=username,brand__brand__contains=btnlist[0]).order_by('brand').values('brand__brand','margin')
            for i in dcardproducts:
                dcp=rcardProducts.objects.filter(brand__brand=i["brand__brand"],status=True).order_by('brand').values('brand').annotate(count=Count('brand')).values('count','brand__id','brand__brand','brand__description','brand__denomination','brand__logo','count','brand__currency')
                if(len(dcp)>0):
                    cost=getRcardProductCost(username,dcp[0]["brand__brand"])
                    data={'brand__id':dcp[0]['brand__id'],'brand__brand':dcp[0]['brand__brand'],'brand__logo':dcp[0]['brand__logo'],'brand__description':dcp[0]['brand__description'],'brand__currency':dcp[0]['brand__currency'],'count':dcp[0]['count'],'cost':cost}
                    content.append(data)
                else:
                    pass
        return render(request,"user/rcard/rcardstore.html",{'dcardproducts':content,'btnlist':btnlist,'user':user,'ads':ads})
    else:
        return redirect(LoginPage)

def userfilterrcardstore(request,brand):
    if request.session.has_key("user"):
        #print(brand)
        username=request.session["user"]
        ads = adverisements.objects.filter(adtype="Image",usertype="User",ctype="Rcard").order_by('-id')[:10]
        user = UserData.objects.get(username=username)
        btnlist=list()
        dproducts = rcardAssignments.objects.filter(assignedto=username).order_by('brand').values('brand__brand','margin')
        for i in dproducts:
            buttons=(i["brand__brand"]).split(" ")
            if buttons[0] not in btnlist:
                btnlist.append(buttons[0])
        dcardproducts = rcardAssignments.objects.filter(assignedto=username,brand__brand__contains=brand).order_by('brand').values('brand__brand','margin')
        content=list()
        #print(buttons)
        for i in dcardproducts:
            dcp=rcardProducts.objects.filter(brand__brand=i["brand__brand"],status=True).order_by('brand').values('brand').annotate(count=Count('brand')).values('count','brand__id','brand__brand','brand__description','brand__denomination','brand__logo','count','brand__currency')
            if(len(dcp)>0):
                cost=getRcardProductCost(username,dcp[0]["brand__brand"])
                data={'brand__id':dcp[0]['brand__id'],'brand__brand':dcp[0]['brand__brand'],'brand__logo':dcp[0]['brand__logo'],'brand__description':dcp[0]['brand__description'],'brand__currency':dcp[0]['brand__currency'],'count':dcp[0]['count'],'cost':cost}
                content.append(data)
            else:
                pass
        return render(request,"user/rcard/rcardstore.html",{'dcardproducts':content,'btnlist':btnlist,'user':user,'ads':ads})
    else:
        return redirect(LoginPage)

def user_buy_rcard_brands(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            username=request.session["user"]
            brand = request.POST.get('brandid', None)
            quantity = request.POST.get('quantity', None)
            amt = request.POST.get('amt', None)
            branddet=rcardBrands.objects.get(brand=brand)
            userdet=UserData.objects.get(username=request.session["user"])
            ctime=datetime.now()
            time = timedelta(minutes = 5)
            now_minus_5 = ctime - time
            checkqty=rcardProducts.objects.filter(Q(brand__brand=brand) & Q(status=True) & (Q(sdate__isnull=True) | Q(sdate__lte=now_minus_5))).values('brand').annotate(productcount=Count('brand')).values('productcount')
            print(checkqty)
            needamt=0;
            result=list()
            content=dict()
            licheckqty=list(checkqty)
            brand_id=0
            deno=0
            if(licheckqty[0]['productcount'] >= int(quantity)):
                usertype=''
                marginlist=list()
                margins=0
                count=0;
                flag=True
                prdct_id=''
                mllist=list()
                sponserlist=list()
                prdctdet = rcardProducts.objects.filter(Q(brand__brand=brand) & Q(status=True) & (Q(sdate__isnull=True) | Q(sdate__lte=now_minus_5)))[:int(quantity)]
                ctime = datetime.now()
                for i in prdctdet:
                    i.productstatus=1
                    i.suser = userdet
                    i.sdate = ctime
                    i.save()
                count=0
                admin=''
                while(True):
                    userdet2=UserData.objects.filter(username=username).values('sponserId','postId','balance')
                    margindet=rcardAssignments.objects.filter(assignedto=username,brand__brand=brand).values('margin')
                    if(userdet2[0]['postId']=="Admin"):
                        admin=username
                        break;
                    else:
                        cost=Decimal(amt)
                        prdctcost = (cost*Decimal(quantity))-(Decimal(margins)*Decimal(quantity))
                        margins=margins+Decimal(margindet[0]['margin'])
                        #print(prdctcost)
                        #print(cost)
                        if(userdet2[0]['balance']>=prdctcost):
                            data={'margin':margindet[0]['margin'],'balance':userdet2[0]['balance'],'username':username,'prdctcost':prdctcost}
                            marginlist.append(data)
                            mllist.append(margindet[0]['margin'])
                            sponserlist.append(username)
                        else:
                            flag=False
                            print(flag)
                            break;
                    username=userdet2[0]['sponserId']
                if(flag):
                    try:
                        prdctcddet=rcardProducts.objects.filter(brand__brand=brand,status=True,productstatus=1,suser=userdet,sdate=ctime)[:int(quantity)]
                        for h in prdctcddet:
                            h.status=False
                            h.save()
                            brand_id=h.brand.id
                            deno=h.brand.denomination
                            prdct_id=prdct_id+""+str(h.id)+","
                            res={"productid":h.id,"carduname":h.username,'brand':h.brand.brand,'brand_logo':h.brand.logo.url, 'status':h.status,'suser':username,'sdate':h.sdate}
                            result.append(res)
                        ml=marginlist[::-1]
                        for k in ml:
                            uname = k['username']
                            margin = k['margin']
                            balance = k['balance']
                            pcost = k['prdctcost']
                            cb=Decimal(balance)-Decimal(pcost)
                            userd=UserData.objects.get(username=uname)
                            userd.balance=cb
                            userd.save()
                        mllen = len(mllist)
                        closeuser=UserData.objects.get(username=request.session["user"])
                        vcrep=vcloudtransactions()
                        vcrep.saleduser = userdet
                        vcrep.brand = brand
                        vcrep.type = "Rcard"
                        vcrep.brand_id = brand_id
                        vcrep.product_id = prdct_id
                        vcrep.quantity = quantity
                        vcrep.obalance = userdet.balance
                        vcrep.cbalance = closeuser.balance
                        vcrep.amount = amt
                        vcrep.rtype = "Web"
                        vcrep.denominations = deno
                        ms = mllist[::-1]
                        mu = sponserlist[::-1]
                        ad=UserData.objects.get(username=admin)
                        if(mllen==1):
                            vcrep.margin1=ms[0]
                            vcrep.sponser1=ad
                            vcrep.sponser2=UserData.objects.get(username=sponserlist[0])
                        elif(mllen==2):
                            vcrep.margin1=ms[0]
                            vcrep.margin2=ms[1]
                            vcrep.sponser1=ad
                            vcrep.sponser2=UserData.objects.get(username=sponserlist[1])
                            vcrep.sponser3=UserData.objects.get(username=sponserlist[0])
                        else:
                            vcrep.margin1=ms[0]
                            vcrep.margin2=ms[1]
                            vcrep.margin3=ms[2]
                            vcrep.sponser1=ad
                            vcrep.sponser2=UserData.objects.get(username=sponserlist[2])
                            vcrep.sponser3=UserData.objects.get(username=sponserlist[1])
                            vcrep.sponser4=UserData.objects.get(username=sponserlist[0])
                        vcrep.save()
                        obj = vcloudtransactions.objects.latest('id')
                        print(obj.id)
                        content["data"] = result
                        content["res_status"]="success"
                        content["trid"]=obj.id
                    except:
                        content["res_status"]="Failed"
                else:
                    for i in prdctdet:
                        i.suser=None
                        i.save()
                    content["res_status"]="Failed"
            return JsonResponse(content,safe=False)
        else:
            return redirect(userrcardstore)
    else:
        return redirect(LoginPage)

def userrcardviewbrands(request):
    if request.session.has_key("user"):
        if request.session.has_key("user"):
            username = request.session["user"]
            vcdprod=rcardBrands.objects.all()
            resultlist=list()
            statuslist=list()
            for i in vcdprod:
                vca=rcardAssignments.objects.filter(assignedto=username,brand__brand=i.brand)
                if not vca:
                    statuslist.append(False)
                else:
                    statuslist.append(True)
            vcd=list(vcdprod)
            print(vcd)
            print(statuslist)
            #print(data)
            ldb=zip(vcd,statuslist)
            userdetails = UserData.objects.get(username=request.session["user"])
            return render(request,"user/rcard/viewBrands.html",{'pdcts':list(ldb),'user':userdetails})
        else:
            return redirect(LoginPage)

def usereditProfilercard(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            user = request.session["user"]
            name = request.POST.get('name', None)
            address = request.POST.get('address', None)
            email = request.POST.get('email', None)
            mobileno = request.POST.get('mobileno', None)
            userDet = UserData.objects.get(username=user)
            userDet.name = name
            userDet.address = address
            userDet.email = email
            userDet.mobileno = mobileno
            userDet.save()
            messages.success(request, 'Successfully Updated')
            return redirect(subresellerprofilercard)
        else:
            messages.warning(request,'Internal Error Occured')
            return redirect(subresellerprofilercard)
    else:
        return redirect(LoginPage)


#________________Need To Host_______________

def addcsvProduct(request):
    if request.session.has_key("user"):
        user=request.session["user"]
        userdet=UserData.objects.get(username=user)
        brands=vcloudBrands.objects.values('id','brand')
        vlogs=vclouduplogs.objects.all().order_by('-cdate');
        return render(request,"admin/vcloud/addcsvproduct.html",{'form':addvcloudproductascsv,'brands':brands,'user':userdet,'vlogs':vlogs})
    else:
        return redirect(LoginPage)

def vcloudcsvupload(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            try:
                form = addvcloudproductascsv(request.POST, request.FILES)
                if form.is_valid():
                    brand = form.cleaned_data.get("brand")
                    csvfile = request.FILES['filename']
                    print(csvfile.name)
                    filedata = csvfile.read().decode("utf-8")
                    lines = filedata.split("\r\n")
                    scount=0
                    pcount=0
                    content=list()
                    count=0
                    for line in lines:
                        print(line)
                        if(line!=''):
                            count=count+1
                            print(count)
                            flag=True
                            fields = line.split(",")
                            data_dict = {}
                            print(fields[0])
                            print(fields[1])
                            data_dict["username"] = fields[0]
                            data_dict["password"] = fields[1]
                            res=vcloudProducts.objects.filter(username = data_dict["username"]).exists()
                            print(res)
                            res1=vcloudupproducts.objects.filter(username = data_dict["username"]).exists()
                            #print(res2)
                            if(res==True or res1==True):
                                print(res)
                                print(res1)
                                pcount=pcount+1
                                print("Exist");
                                print("------------")
                                print(data_dict["username"])
                            else:
                                pcount=pcount+1
                                scount=scount+1
                                content.append(data_dict)
                                print(res)
                                print(res1)
                                print("Not Exist")
                        else:
                            pass
                            #print(data_dict["username"])
                        #print(flag)
                    print(content)
                    print(scount)
                    print(pcount)
                    user = UserData.objects.get(username=request.session["user"])
                    bd = vcloudBrands.objects.get(id=brand)
                    #print(bd.id)
                    vclog=vclouduplogs()
                    vclog.brand = bd
                    vclog.user = user
                    vclog.file = csvfile
                    vclog.scount = scount
                    vclog.pcount = pcount
                    vclog.save()
                    lid=vclouduplogs.objects.latest('id')
                    #print(lid.id)
                    vcpbj=vclouduplogs.objects.get(id=lid.id)
                    #print(vcpbj)

                    for item in content:
                        print(item["username"]);
                        vcpd=vcloudupproducts()
                        vcpd.fileid=vcpbj
                        vcpd.brand=bd
                        vcpd.denomination=bd.denomination
                        vcpd.username=item["username"]
                        vcpd.password=item["password"]
                        vcpd.save()
                    messages.success(request,"SuccessFully Added The Csv")
                else:
                    messages.warning(request,form.errors)
                    return redirect(addcsvProduct)
            except Exception as e:
                print(e)
                messages.warning(request,form.errors)
                return redirect(addcsvProduct)
        return redirect(addcsvProduct)
    else:
        return redirect(LoginPage)

def vcloudlogtoproduct(request,id):
    if request.session.has_key("user"):
        print(id)
        vlog = vclouduplogs.objects.get(id=id)
        vcprod = vcloudupproducts.objects.filter(fileid=vlog.id)
        for item in vcprod:
            vcprd=vcloudProducts()
            vcprd.brand=vlog.brand
            vcprd.username=item.username
            vcprd.password=item.password
            vcprd.denomination=item.denomination
            vcprd.fileid=vlog
            vcprd.save()
        vlog.status=False
        vlog.sdate=datetime.now()
        vlog.save()
        return redirect(addcsvProduct)
    else:
        return redirect(addcsvProduct)


def adddcardcsvProduct(request):
    if request.session.has_key("user"):
        user=request.session["user"]
        userdet=UserData.objects.get(username=user)
        brands=dcardBrands.objects.values('id','brand')
        vlogs=dcarduplogs.objects.all().order_by('-cdate');
        return render(request,"admin/dcard/addcsvproduct.html",{'form':adddcardproductascsv,'brands':brands,'user':userdet,'vlogs':vlogs})
    else:
        return redirect(LoginPage)

def dcardcsvupload(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = adddcardproductascsv(request.POST, request.FILES)
            if form.is_valid():
                brand = form.cleaned_data.get("brand")
                csvfile = request.FILES['filename']
                print(csvfile.name)
                filedata = csvfile.read().decode("utf-8")
                lines = filedata.split("\r\n")
                scount=0
                pcount=0
                content=list()
                for line in lines:
                    if(line != ''):
                        fields = line.split(",")
                        data_dict = {}
                        data_dict["username"] = fields[0]
                        res=datacardproducts.objects.filter(username = data_dict["username"]).exists()
                        print(res)
                        res2=dcardupproducts.objects.filter(username = data_dict["username"]).exists()
                        print(res2)
                        if(res==True or  res2==True):
                            pcount=pcount+1
                        else:
                            pcount=pcount+1
                            scount=scount+1
                            content.append(data_dict)
                    else:
                        pass
                #print(brand)
                print(content)
                user = UserData.objects.get(username=request.session["user"])
                bd = dcardBrands.objects.get(id=int(brand))
                print(bd.id)
                vclog=dcarduplogs()
                vclog.brand = bd
                vclog.user = user
                vclog.file = csvfile
                vclog.scount = scount
                vclog.pcount = pcount
                vclog.save()
                lid=dcarduplogs.objects.latest('id')
                print(lid.id)
                vcpbj=dcarduplogs.objects.get(id=lid.id)
                print(vcpbj)
                for item in content:
                    vcpd=dcardupproducts()
                    vcpd.fileid=vcpbj
                    vcpd.brand=bd
                    vcpd.denomination=bd.denomination
                    vcpd.username = item["username"]
                    vcpd.save()
                messages.success(request,"SuccessFully Added The Csv")
            else:
                messages.warning(request,form.errors)
                return redirect(adddcardcsvProduct)
        return redirect(adddcardcsvProduct)
    else:
        return redirect(LoginPage)

def dcardlogtoproduct(request,id):
    if request.session.has_key("user"):
        print(id)
        vlog = dcarduplogs.objects.get(id=id)
        vcprod = dcardupproducts.objects.filter(fileid=vlog.id)
        for item in vcprod:
            vcprd=datacardproducts()
            vcprd.brand=vlog.brand
            vcprd.username=item.username
            vcprd.denomination=item.denomination
            vcprd.fileid=vlog
            vcprd.save()
        vlog.status=False
        vlog.sdate=datetime.now()
        vlog.save()
        return redirect(adddcardcsvProduct)
    else:
        return redirect(adddcardcsvProduct)

def addrcardcsvProduct(request):
    if request.session.has_key("user"):
        user=request.session["user"]
        userdet=UserData.objects.get(username=user)
        brands=rcardBrands.objects.values('id','brand')
        vlogs=rcarduplogs.objects.all().order_by('-cdate');
        return render(request,"admin/rcard/addcsvproduct.html",{'form':addrcardproductascsv,'brands':brands,'user':userdet,'vlogs':vlogs})
    else:
        return redirect(LoginPage)

def rcardcsvupload(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = addrcardproductascsv(request.POST, request.FILES)
            if form.is_valid():
                brand = form.cleaned_data.get("brand")
                csvfile = request.FILES['filename']
                print(csvfile.name)
                filedata = csvfile.read().decode("utf-8")
                lines = filedata.split("\r\n")
                scount=0
                pcount=0
                content=list()
                for line in lines:
                    if(line!=''):
                        fields = line.split(",")
                        data_dict = {}
                        data_dict["username"] = fields[0]
                        res=rcardProducts.objects.filter(username = data_dict["username"]).exists()
                        print(res)
                        res2=rcardupproducts.objects.filter(username = data_dict["username"]).exists()
                        print(res2)
                        if(res==True or res2==True):
                            print(fields[0])
                            pcount=pcount+1
                        else:
                            pcount=pcount+1
                            scount=scount+1
                            content.append(data_dict)
                    else:
                        pass
                print(content)
                user = UserData.objects.get(username=request.session["user"])
                bd = rcardBrands.objects.get(id=int(brand))
                print(bd.id)
                vclog=rcarduplogs()
                vclog.brand = bd
                vclog.user = user
                vclog.file = csvfile
                vclog.scount = scount
                vclog.pcount = pcount
                vclog.save()
                lid=rcarduplogs.objects.latest('id')
                print(lid.id)
                vcpbj=rcarduplogs.objects.get(id=lid.id)
                print(vcpbj)
                for item in content:
                    vcpd=rcardupproducts()
                    vcpd.fileid=vcpbj
                    vcpd.brand=bd
                    vcpd.denomination=bd.denomination
                    vcpd.username=item["username"]
                    vcpd.save()
                messages.success(request,"SuccessFully Added The Csv")
            else:
                messages.warning(request,form.errors)
                return redirect(addrcardcsvProduct)
        return redirect(addrcardcsvProduct)
    else:
        return redirect(LoginPage)

def rcardlogtoproduct(request,id):
    if request.session.has_key("user"):
        #print(id)
        vlog = rcarduplogs.objects.get(id=id)
        vcprod = rcardupproducts.objects.filter(fileid=vlog.id)
        for item in vcprod:
            vcprd=rcardProducts()
            vcprd.brand=vlog.brand
            vcprd.username=item.username
            vcprd.denomination=item.denomination
            vcprd.fileid=vlog
            vcprd.save()
        vlog.status=False
        vlog.sdate=datetime.now()
        vlog.save()
        return redirect(addrcardcsvProduct)
    else:
        return redirect(addrcardcsvProduct)

def vcloudchangepassword(request):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=request.session["user"])
        return render(request,"admin/vcloud/changepassword.html",{'form':changepassword,'user':userdet})
    else:
        return redirect(LoginPage)

def submitvcloudchangepassword(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            form = changepassword(request.POST or None)
            if form.is_valid():
                username = request.session["user"]
                cpassword = form.cleaned_data.get("cpassword")
                npassword = form.cleaned_data.get("npassword")
                cnpassword = form.cleaned_data.get("cnpassword")
                if(npassword==cnpassword):
                    hashkey = username+cpassword
                    hash = hashlib.sha256(hashkey.encode()).hexdigest()
                    if (UserData.objects.filter(username = username, password = hash)).exists():
                        user = UserData.objects.get(username = username, password = hash)
                        newhashkey = username+npassword
                        newhash = hashlib.sha256(newhashkey.encode()).hexdigest()
                        user.password=newhash
                        user.save()
                        messages.success(request,"Password Changed Successfully.!")
                        return redirect(vcloudchangepassword)
                    else:
                        messages.warning(request,"Incorrect Password, Try Again.!")
                        return redirect(vcloudchangepassword)
                else:
                    messages.warning(request,"Passwords Are Not Matching.!")
                    return redirect(vcloudchangepassword)
            else:
                messages.warning(request,form.errors)
                return redirect(vcloudchangepassword)
        else:
            return redirect(vcloudchangepassword)
    else:
        return(LoginPage)

def dcardchangepassword(request):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=request.session["user"])
        return render(request,"admin/dcard/changepassword.html",{'form':changepassword,'user':userdet})
    else:
        return redirect(LoginPage)

def submitdcardchangepassword(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            form = changepassword(request.POST or None)
            if form.is_valid():
                username = request.session["user"]
                cpassword = form.cleaned_data.get("cpassword")
                npassword = form.cleaned_data.get("npassword")
                cnpassword = form.cleaned_data.get("cnpassword")
                if(npassword==cnpassword):
                    hashkey = username+cpassword
                    hash = hashlib.sha256(hashkey.encode()).hexdigest()
                    if (UserData.objects.filter(username = username, password = hash)).exists():
                        user = UserData.objects.get(username = username, password = hash)
                        newhashkey = username+npassword
                        newhash = hashlib.sha256(newhashkey.encode()).hexdigest()
                        user.password=newhash
                        user.save()
                        messages.success(request,"Password Changed Successfully.!")
                        return redirect(dcardchangepassword)
                    else:
                        messages.warning(request,"Incorrect Password, Try Again.!")
                        return redirect(dcardchangepassword)
                else:
                    messages.warning(request,"Passwords Are Not Matching.!")
                    return redirect(dcardchangepassword)
            else:
                messages.warning(request,form.errors)
                return redirect(dcardchangepassword)
        else:
            return redirect(dcardchangepassword)
    else:
        return(LoginPage)

def rcardchangepassword(request):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=request.session["user"])
        return render(request,"admin/rcard/changepassword.html",{'form':changepassword,'user':userdet})
    else:
        return redirect(LoginPage)

def submitrcardchangepassword(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            form = changepassword(request.POST or None)
            if form.is_valid():
                username = request.session["user"]
                cpassword = form.cleaned_data.get("cpassword")
                npassword = form.cleaned_data.get("npassword")
                cnpassword = form.cleaned_data.get("cnpassword")
                if(npassword==cnpassword):
                    hashkey = username+cpassword
                    hash = hashlib.sha256(hashkey.encode()).hexdigest()
                    if (UserData.objects.filter(username = username, password = hash)).exists():
                        user = UserData.objects.get(username = username, password = hash)
                        newhashkey = username+npassword
                        newhash = hashlib.sha256(newhashkey.encode()).hexdigest()
                        user.password=newhash
                        user.save()
                        messages.success(request,"Password Changed Successfully.!")
                        return redirect(rcardchangepassword)
                    else:
                        messages.warning(request,"Incorrect Password, Try Again.!")
                        return redirect(rcardchangepassword)
                else:
                    messages.warning(request,"Passwords Are Not Matching.!")
                    return redirect(rcardchangepassword)
            else:
                messages.warning(request,form.errors)
                return redirect(rcardchangepassword)
        else:
            return redirect(rcardchangepassword)
    else:
        return(LoginPage)

def resellervcloudchangepassword(request):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=request.session["user"])
        return render(request,"reseller/vcloud/changepassword.html",{'form':changepassword,'user':userdet})
    else:
        return redirect(LoginPage)

def resellersubmitvcloudchangepassword(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            form = changepassword(request.POST or None)
            if form.is_valid():
                username = request.session["user"]
                cpassword = form.cleaned_data.get("cpassword")
                npassword = form.cleaned_data.get("npassword")
                cnpassword = form.cleaned_data.get("cnpassword")
                if(npassword==cnpassword):
                    hashkey = username+cpassword
                    hash = hashlib.sha256(hashkey.encode()).hexdigest()
                    if (UserData.objects.filter(username = username, password = hash)).exists():
                        user = UserData.objects.get(username = username, password = hash)
                        newhashkey = username+npassword
                        newhash = hashlib.sha256(newhashkey.encode()).hexdigest()
                        user.password=newhash
                        user.save()
                        messages.success(request,"Password Changed Successfully.!")
                        return redirect(resellervcloudchangepassword)
                    else:
                        messages.warning(request,"Incorrect Password, Try Again.!")
                        return redirect(resellervcloudchangepassword)
                else:
                    messages.warning(request,"Passwords Are Not Matching.!")
                    return redirect(resellervcloudchangepassword)
            else:
                messages.warning(request,form.errors)
                return redirect(resellervcloudchangepassword)
        else:
            return redirect(resellervcloudchangepassword)
    else:
        return(LoginPage)

def resellerdcardchangepassword(request):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=request.session["user"])
        return render(request,"reseller/dcard/changepassword.html",{'form':changepassword,'user':userdet})
    else:
        return redirect(LoginPage)

def resellersubmitdcardchangepassword(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            form = changepassword(request.POST or None)
            if form.is_valid():
                username = request.session["user"]
                cpassword = form.cleaned_data.get("cpassword")
                npassword = form.cleaned_data.get("npassword")
                cnpassword = form.cleaned_data.get("cnpassword")
                if(npassword==cnpassword):
                    hashkey = username+cpassword
                    hash = hashlib.sha256(hashkey.encode()).hexdigest()
                    if (UserData.objects.filter(username = username, password = hash)).exists():
                        user = UserData.objects.get(username = username, password = hash)
                        newhashkey = username+npassword
                        newhash = hashlib.sha256(newhashkey.encode()).hexdigest()
                        user.password=newhash
                        user.save()
                        messages.success(request,"Password Changed Successfully.!")
                        return redirect(resellerdcardchangepassword)
                    else:
                        messages.warning(request,"Incorrect Password, Try Again.!")
                        return redirect(resellerdcardchangepassword)
                else:
                    messages.warning(request,"Passwords Are Not Matching.!")
                    return redirect(resellerdcardchangepassword)
            else:
                messages.warning(request,form.errors)
                return redirect(resellerdcardchangepassword)
        else:
            return redirect(resellerdcardchangepassword)
    else:
        return(LoginPage)

def resellerrcardchangepassword(request):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=request.session["user"])
        return render(request,"reseller/rcard/changepassword.html",{'form':changepassword,'user':userdet})
    else:
        return redirect(LoginPage)

def resellersubmitrcardchangepassword(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            form = changepassword(request.POST or None)
            if form.is_valid():
                username = request.session["user"]
                cpassword = form.cleaned_data.get("cpassword")
                npassword = form.cleaned_data.get("npassword")
                cnpassword = form.cleaned_data.get("cnpassword")
                if(npassword==cnpassword):
                    hashkey = username+cpassword
                    hash = hashlib.sha256(hashkey.encode()).hexdigest()
                    if (UserData.objects.filter(username = username, password = hash)).exists():
                        user = UserData.objects.get(username = username, password = hash)
                        newhashkey = username+npassword
                        newhash = hashlib.sha256(newhashkey.encode()).hexdigest()
                        user.password=newhash
                        user.save()
                        messages.success(request,"Password Changed Successfully.!")
                        return redirect(resellerrcardchangepassword)
                    else:
                        messages.warning(request,"Incorrect Password, Try Again.!")
                        return redirect(resellerrcardchangepassword)
                else:
                    messages.warning(request,"Passwords Are Not Matching.!")
                    return redirect(resellerrcardchangepassword)
            else:
                messages.warning(request,form.errors)
                return redirect(resellerrcardchangepassword)
        else:
            return redirect(resellerrcardchangepassword)
    else:
        return(LoginPage)

def subresellervcloudchangepassword(request):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=request.session["user"])
        return render(request,"sub_reseller/vcloud/changepassword.html",{'form':changepassword,'user':userdet})
    else:
        return redirect(LoginPage)

def subresellersubmitvcloudchangepassword(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            form = changepassword(request.POST or None)
            if form.is_valid():
                username = request.session["user"]
                cpassword = form.cleaned_data.get("cpassword")
                npassword = form.cleaned_data.get("npassword")
                cnpassword = form.cleaned_data.get("cnpassword")
                if(npassword==cnpassword):
                    hashkey = username+cpassword
                    hash = hashlib.sha256(hashkey.encode()).hexdigest()
                    if (UserData.objects.filter(username = username, password = hash)).exists():
                        user = UserData.objects.get(username = username, password = hash)
                        newhashkey = username+npassword
                        newhash = hashlib.sha256(newhashkey.encode()).hexdigest()
                        user.password=newhash
                        user.save()
                        messages.success(request,"Password Changed Successfully.!")
                        return redirect(subresellervcloudchangepassword)
                    else:
                        messages.warning(request,"Incorrect Password, Try Again.!")
                        return redirect(subresellervcloudchangepassword)
                else:
                    messages.warning(request,"Passwords Are Not Matching.!")
                    return redirect(subresellervcloudchangepassword)
            else:
                messages.warning(request,form.errors)
                return redirect(subresellervcloudchangepassword)
        else:
            return redirect(subresellervcloudchangepassword)
    else:
        return(LoginPage)

def subresellerdcardchangepassword(request):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=request.session["user"])
        return render(request,"sub_reseller/dcard/changepassword.html",{'form':changepassword,'user':userdet})
    else:
        return redirect(LoginPage)

def subresellersubmitdcardchangepassword(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            form = changepassword(request.POST or None)
            if form.is_valid():
                username = request.session["user"]
                cpassword = form.cleaned_data.get("cpassword")
                npassword = form.cleaned_data.get("npassword")
                cnpassword = form.cleaned_data.get("cnpassword")
                if(npassword==cnpassword):
                    hashkey = username+cpassword
                    hash = hashlib.sha256(hashkey.encode()).hexdigest()
                    if (UserData.objects.filter(username = username, password = hash)).exists():
                        user = UserData.objects.get(username = username, password = hash)
                        newhashkey = username+npassword
                        newhash = hashlib.sha256(newhashkey.encode()).hexdigest()
                        user.password=newhash
                        user.save()
                        messages.success(request,"Password Changed Successfully.!")
                        return redirect(subresellerdcardchangepassword)
                    else:
                        messages.warning(request,"Incorrect Password, Try Again.!")
                        return redirect(subresellerdcardchangepassword)
                else:
                    messages.warning(request,"Passwords Are Not Matching.!")
                    return redirect(subresellerdcardchangepassword)
            else:
                messages.warning(request,form.errors)
                return redirect(subresellerdcardchangepassword)
        else:
            return redirect(subresellerdcardchangepassword)
    else:
        return(LoginPage)

def subresellerrcardchangepassword(request):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=request.session["user"])
        return render(request,"sub_reseller/rcard/changepassword.html",{'form':changepassword,'user':userdet})
    else:
        return redirect(LoginPage)

def subresellersubmitrcardchangepassword(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            form = changepassword(request.POST or None)
            if form.is_valid():
                username = request.session["user"]
                cpassword = form.cleaned_data.get("cpassword")
                npassword = form.cleaned_data.get("npassword")
                cnpassword = form.cleaned_data.get("cnpassword")
                if(npassword==cnpassword):
                    hashkey = username+cpassword
                    hash = hashlib.sha256(hashkey.encode()).hexdigest()
                    if (UserData.objects.filter(username = username, password = hash)).exists():
                        user = UserData.objects.get(username = username, password = hash)
                        newhashkey = username+npassword
                        newhash = hashlib.sha256(newhashkey.encode()).hexdigest()
                        user.password=newhash
                        user.save()
                        messages.success(request,"Password Changed Successfully.!")
                        return redirect(subresellerrcardchangepassword)
                    else:
                        messages.warning(request,"Incorrect Password, Try Again.!")
                        return redirect(subresellerrcardchangepassword)
                else:
                    messages.warning(request,"Passwords Are Not Matching.!")
                    return redirect(subresellerrcardchangepassword)
            else:
                messages.warning(request,form.errors)
                return redirect(subresellerrcardchangepassword)
        else:
            return redirect(subresellerrcardchangepassword)
    else:
        return(LoginPage)

def uservcloudchangepassword(request):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=request.session["user"])
        return render(request,"user/vcloud/changepassword.html",{'form':changepassword,'user':userdet})
    else:
        return redirect(LoginPage)

def usersubmitvcloudchangepassword(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            form = changepassword(request.POST or None)
            if form.is_valid():
                username = request.session["user"]
                cpassword = form.cleaned_data.get("cpassword")
                npassword = form.cleaned_data.get("npassword")
                cnpassword = form.cleaned_data.get("cnpassword")
                if(npassword==cnpassword):
                    hashkey = username+cpassword
                    hash = hashlib.sha256(hashkey.encode()).hexdigest()
                    if (UserData.objects.filter(username = username, password = hash)).exists():
                        user = UserData.objects.get(username = username, password = hash)
                        newhashkey = username+npassword
                        newhash = hashlib.sha256(newhashkey.encode()).hexdigest()
                        user.password=newhash
                        user.save()
                        messages.success(request,"Password Changed Successfully.!")
                        return redirect(uservcloudchangepassword)
                    else:
                        messages.warning(request,"Incorrect Password, Try Again.!")
                        return redirect(uservcloudchangepassword)
                else:
                    messages.warning(request,"Passwords Are Not Matching.!")
                    return redirect(uservcloudchangepassword)
            else:
                messages.warning(request,form.errors)
                return redirect(uservcloudchangepassword)
        else:
            return redirect(uservcloudchangepassword)
    else:
        return(LoginPage)

def userdcardchangepassword(request):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=request.session["user"])
        return render(request,"user/dcard/changepassword.html",{'form':changepassword,'user':userdet})
    else:
        return redirect(LoginPage)

def usersubmitdcardchangepassword(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            form = changepassword(request.POST or None)
            if form.is_valid():
                username = request.session["user"]
                cpassword = form.cleaned_data.get("cpassword")
                npassword = form.cleaned_data.get("npassword")
                cnpassword = form.cleaned_data.get("cnpassword")
                if(npassword==cnpassword):
                    hashkey = username+cpassword
                    hash = hashlib.sha256(hashkey.encode()).hexdigest()
                    if (UserData.objects.filter(username = username, password = hash)).exists():
                        user = UserData.objects.get(username = username, password = hash)
                        newhashkey = username+npassword
                        newhash = hashlib.sha256(newhashkey.encode()).hexdigest()
                        user.password=newhash
                        user.save()
                        messages.success(request,"Password Changed Successfully.!")
                        return redirect(userdcardchangepassword)
                    else:
                        messages.warning(request,"Incorrect Password, Try Again.!")
                        return redirect(userdcardchangepassword)
                else:
                    messages.warning(request,"Passwords Are Not Matching.!")
                    return redirect(userdcardchangepassword)
            else:
                messages.warning(request,form.errors)
                return redirect(userdcardchangepassword)
        else:
            return redirect(userdcardchangepassword)
    else:
        return(LoginPage)

def userrcardchangepassword(request):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=request.session["user"])
        return render(request,"user/rcard/changepassword.html",{'form':changepassword,'user':userdet})
    else:
        return redirect(LoginPage)

def usersubmitrcardchangepassword(request):
    if request.session.has_key("user"):
        if request.method=="POST":
            form = changepassword(request.POST or None)
            if form.is_valid():
                username = request.session["user"]
                cpassword = form.cleaned_data.get("cpassword")
                npassword = form.cleaned_data.get("npassword")
                cnpassword = form.cleaned_data.get("cnpassword")
                if(npassword==cnpassword):
                    hashkey = username+cpassword
                    hash = hashlib.sha256(hashkey.encode()).hexdigest()
                    if (UserData.objects.filter(username = username, password = hash)).exists():
                        user = UserData.objects.get(username = username, password = hash)
                        newhashkey = username+npassword
                        newhash = hashlib.sha256(newhashkey.encode()).hexdigest()
                        user.password=newhash
                        user.save()
                        messages.success(request,"Password Changed Successfully.!")
                        return redirect(userrcardchangepassword)
                    else:
                        messages.warning(request,"Incorrect Password, Try Again.!")
                        return redirect(userrcardchangepassword)
                else:
                    messages.warning(request,"Passwords Are Not Matching.!")
                    return redirect(userrcardchangepassword)
            else:
                messages.warning(request,form.errors)
                return redirect(userrcardchangepassword)
        else:
            return redirect(userrcardchangepassword)
    else:
        return(LoginPage)

def resetpasswordvcloudreseller(request,username):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=username)
        password=username
        hashkey = username+password
        newhash = hashlib.sha256(hashkey.encode()).hexdigest()
        userdet.password=newhash
        userdet.save()
        print(username)
    return redirect(vcloudviewReseller)

def resetpasswordvclouduser(request,username):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=username)
        password=username
        hashkey = username+password
        newhash = hashlib.sha256(hashkey.encode()).hexdigest()
        userdet.password=newhash
        userdet.save()
        print(username)
    return redirect(vcloudviewUser)

def resetpassworddcardreseller(request,username):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=username)
        password=username
        hashkey = username+password
        newhash = hashlib.sha256(hashkey.encode()).hexdigest()
        userdet.password=newhash
        userdet.save()
        print(username)
    return redirect(dcardviewReseller)



def resetpassworddcarduser(request,username):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=username)
        password=username
        hashkey = username+password
        newhash = hashlib.sha256(hashkey.encode()).hexdigest()
        userdet.password=newhash
        userdet.save()
        print(username)
    return redirect(dcardviewUser)

def resetpasswordrcardreseller(request,username):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=username)
        password=username
        hashkey = username+password
        newhash = hashlib.sha256(hashkey.encode()).hexdigest()
        userdet.password=newhash
        userdet.save()
        print(username)
    return redirect(rcardviewReseller)

def resetpasswordrcarduser(request,username):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=username)
        password=username
        hashkey = username+password
        newhash = hashlib.sha256(hashkey.encode()).hexdigest()
        userdet.password=newhash
        userdet.save()
        print(username)
    return redirect(rcardviewUser)

def resetpasswordresellervcloudreseller(request,username):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=username)
        password=username
        hashkey = username+password
        newhash = hashlib.sha256(hashkey.encode()).hexdigest()
        userdet.password=newhash
        userdet.save()
        print(username)
    return redirect(resellervcloudviewReseller)

def resetpasswordresellervclouduser(request,username):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=username)
        password=username
        hashkey = username+password
        newhash = hashlib.sha256(hashkey.encode()).hexdigest()
        userdet.password=newhash
        userdet.save()
        print(username)
    return redirect(resellervcloudviewUser)

def resetpasswordresellerdcardreseller(request,username):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=username)
        password=username
        hashkey = username+password
        newhash = hashlib.sha256(hashkey.encode()).hexdigest()
        userdet.password=newhash
        userdet.save()
        print(username)
    return redirect(resellerviewResellerDcard)

def resetpasswordresellerdcarduser(request,username):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=username)
        password=username
        hashkey = username+password
        newhash = hashlib.sha256(hashkey.encode()).hexdigest()
        userdet.password=newhash
        userdet.save()
        print(username)
    return redirect(resellerviewUserDcard)

def resetpasswordresellerrcardreseller(request,username):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=username)
        password=username
        hashkey = username+password
        newhash = hashlib.sha256(hashkey.encode()).hexdigest()
        userdet.password=newhash
        userdet.save()
        print(username)
    return redirect(resellerviewResellerRcard)

def resetpasswordresellerrcarduser(request,username):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=username)
        password=username
        hashkey = username+password
        newhash = hashlib.sha256(hashkey.encode()).hexdigest()
        userdet.password=newhash
        userdet.save()
        print(username)
    return redirect(resellerviewUserRcard)

def resetpasswordsubresellervclouduser(request,username):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=username)
        password=username
        hashkey = username+password
        newhash = hashlib.sha256(hashkey.encode()).hexdigest()
        userdet.password=newhash
        userdet.save()
        print(username)
    return redirect(subresellervcloudviewUser)

def resetpasswordsubresellerdcarduser(request,username):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=username)
        password=username
        hashkey = username+password
        newhash = hashlib.sha256(hashkey.encode()).hexdigest()
        userdet.password=newhash
        userdet.save()
        print(username)
    return redirect(subresellerviewUserDcard)

def vcloudchangeResellerStatus(request,username):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=username)
        if(userdet.status):
            userdet.status=False
            userdet.save()
        else:
            userdet.status=True
            userdet.save()
    return redirect(vcloudviewReseller)

def dcardchangeResellerStatus(request,username):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=username)
        if(userdet.status):
            userdet.status=False
            userdet.save()
        else:
            userdet.status=True
            userdet.save()
    return redirect(dcardviewReseller)

def rcardchangeResellerStatus(request,username):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=username)
        if(userdet.status):
            userdet.status=False
            userdet.save()
        else:
            userdet.status=True
            userdet.save()
    return redirect(rcardviewReseller)

def vcloudchangeUserStatus(request,username):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=username)
        if(userdet.status):
            userdet.status=False
            userdet.save()
        else:
            userdet.status=True
            userdet.save()
    return redirect(vcloudviewUser)

def dcardchangeUserStatus(request,username):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=username)
        if(userdet.status):
            userdet.status=False
            userdet.save()
        else:
            userdet.status=True
            userdet.save()
    return redirect(dcardviewUser)

def rcardchangeUserStatus(request,username):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=username)
        if(userdet.status):
            userdet.status=False
            userdet.save()
        else:
            userdet.status=True
            userdet.save()
    return redirect(rcardviewUser)

def resellervcloudchangeResellerStatus(request,username):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=username)
        if(userdet.status):
            userdet.status=False
            userdet.save()
        else:
            userdet.status=True
            userdet.save()
    return redirect(resellervcloudviewReseller)

def resellerdcardchangeResellerStatus(request,username):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=username)
        if(userdet.status):
            userdet.status=False
            userdet.save()
        else:
            userdet.status=True
            userdet.save()
    return redirect(resellerviewResellerDcard)

def resellerrcardchangeResellerStatus(request,username):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=username)
        if(userdet.status):
            userdet.status=False
            userdet.save()
        else:
            userdet.status=True
            userdet.save()
    return redirect(resellerviewResellerRcard)

def resellervcloudchangeUserStatus(request,username):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=username)
        if(userdet.status):
            userdet.status=False
            userdet.save()
        else:
            userdet.status=True
            userdet.save()
    return redirect(resellervcloudviewUser)

def resellerdcardchangeUserStatus(request,username):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=username)
        if(userdet.status):
            userdet.status=False
            userdet.save()
        else:
            userdet.status=True
            userdet.save()
    return redirect(resellerviewUserDcard)

def resellerrcardchangeUserStatus(request,username):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=username)
        if(userdet.status):
            userdet.status=False
            userdet.save()
        else:
            userdet.status=True
            userdet.save()
    return redirect(resellerviewUserRcard)

def subresellervcloudchangeUserStatus(request,username):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=username)
        if(userdet.status):
            userdet.status=False
            userdet.save()
        else:
            userdet.status=True
            userdet.save()
    return redirect(subresellervcloudviewUser)

def subresellerdcardchangeUserStatus(request,username):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=username)
        if(userdet.status):
            userdet.status=False
            userdet.save()
        else:
            userdet.status=True
            userdet.save()
    return redirect(subresellerviewUserDcard)

def subresellerrcardchangeUserStatus(request,username):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=username)
        if(userdet.status):
            userdet.status=False
            userdet.save()
        else:
            userdet.status=True
            userdet.save()
    return redirect(subresellerviewUserRcard)

def resetpasswordsubresellerrcarduser(request,username):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=username)
        password=username
        hashkey = username+password
        newhash = hashlib.sha256(hashkey.encode()).hexdigest()
        userdet.password=newhash
        userdet.save()
        print(username)
    return redirect(subresellerviewUserRcard)

def vcloudcardsdownloads(request,id):
    print(id)
    image="media/img/card.png"
    img = Image.open(image)
    draw = ImageDraw.Draw(img)
    fontpath = os.path.join(settings.BASE_DIR, "static/pfont/sans_serif.ttf")
    print(fontpath)
    font = ImageFont.truetype(fontpath, 16)
    pddet=vcloudProducts.objects.get(id=id)
    imagelogo=pddet.brand.logo.url
    str=imagelogo.replace("%20", " ")
    print(str)
    logo = str.lstrip('/')
    print(image)
    print(logo)
    draw.text((100, 200),"Owner    : "+pddet.suser.name,(0,0,0),font=font)
    draw.text((100, 230),"Brand    : "+pddet.brand.brand,(0,0,0),font=font)
    draw.text((100, 260),"Username : "+pddet.username,(0,0,0),font=font)
    draw.text((100, 290),"Password : "+pddet.password,(0,0,0),font=font)
    img.save('media/img/sample-out.png')
    dimage = Image.open(os.path.join(settings.MEDIA_ROOT, "img/sample-out.png"))
    print(dimage)

    filename = dimage.filename
    print(filename)
    wrapper = FileWrapper(open(filename,'rb'))
    content_type = mimetypes.guess_type(filename)[0]
    print(content_type)
    response = HttpResponse(wrapper, content_type='content_type')
    response['Content-Disposition'] = "attachment; filename=card.png"
    return response

def dcardcardsdownloads(request,id):
    print(id)
    image="media/img/card.png"
    img = Image.open(image)
    draw = ImageDraw.Draw(img)
    fontpath = os.path.join(settings.BASE_DIR, "static/pfont/sans_serif.ttf")
    print(fontpath)
    font = ImageFont.truetype(fontpath, 16)
    pddet=datacardproducts.objects.get(id=id)
    imagelogo=pddet.brand.logo.url
    str=imagelogo.replace("%20", " ")
    print(str)
    logo = str.lstrip('/')
    print(image)
    print(logo)
    draw.text((100, 200),"Owner    : "+pddet.suser.name,(0,0,0),font=font)
    draw.text((100, 230),"Brand    : "+pddet.brand.brand,(0,0,0),font=font)
    draw.text((100, 260),"Username : "+pddet.username,(0,0,0),font=font)
    #draw.text((100, 290),"Password : "+pddet.password,(255,255,255),font=font)
    img.save('media/img/sample-out.png')
    dimage = Image.open(os.path.join(settings.MEDIA_ROOT, "img/sample-out.png"))
    print(dimage)
    filename = dimage.filename
    print(filename)
    wrapper = FileWrapper(open(filename,'rb'))
    content_type = mimetypes.guess_type(filename)[0]
    print(content_type)
    response = HttpResponse(wrapper, content_type='content_type')
    response['Content-Disposition'] = "attachment; filename=card.png"
    return response

def rcardcardsdownloads(request,id):
    print(id)
    image="media/img/card.png"
    img = Image.open(image)
    draw = ImageDraw.Draw(img)
    fontpath = os.path.join(settings.BASE_DIR, "static/pfont/sans_serif.ttf")
    print(fontpath)
    font = ImageFont.truetype(fontpath, 16)
    pddet=rcardProducts.objects.get(id=id)
    imagelogo=pddet.brand.logo.url
    str=imagelogo.replace("%20", " ")
    print(str)
    logo = str.lstrip('/')
    print(image)
    print(logo)
    draw.text((100, 200),"Owner    : "+pddet.suser.name,(0,0,0),font=font)
    draw.text((100, 230),"Brand    : "+pddet.brand.brand,(0,0,0),font=font)
    draw.text((100, 260),"Username : "+pddet.username,(0,0,0),font=font)
    #draw.text((100, 290),"Password : "+pddet.password,(255,255,255),font=font)
    img.save('media/img/sample-out.png')
    dimage = Image.open(os.path.join(settings.MEDIA_ROOT, "img/sample-out.png"))
    print(dimage)

    filename = dimage.filename
    print(filename)
    wrapper = FileWrapper(open(filename,'rb'))
    content_type = mimetypes.guess_type(filename)[0]
    print(content_type)
    response = HttpResponse(wrapper, content_type='content_type')
    response['Content-Disposition'] = "attachment; filename=card.png"
    return response
    #return redirect(vcloudreport)

def uservcloudpaymentreport(request):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=request.session["user"])
        phist = fundTransactionReport.objects.filter(destination=userdet).order_by('-date')[:40]
        return render(request,"user/vcloud/paymentReport.html",{'form':datefilterform,'user':userdet,'phist':phist})
    else:
        return redirect(LoginPage)

def filteruservcloudpaymentreport(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = datefilterform(request.POST or None)
            print(form.errors)
            if form.is_valid():
                currentuser=request.session["user"]
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                userdet=UserData.objects.get(username=currentuser)
                phist = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdet).order_by('-date')
                return render(request,"user/vcloud/paymentReport.html",{'form':datefilterform,'user':userdet,'phist':phist})
            else:
                return redirect(uservcloudpaymentreport)
        else:
            return redirect(uservcloudpaymentreport)
    else:
        return redirect(LoginPage)

def userdcardpaymentreport(request):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=request.session["user"])
        phist = fundTransactionReport.objects.filter(destination=userdet).order_by('-date')
        return render(request,"user/dcard/paymentReport.html",{'form':datefilterform,'user':userdet,'phist':phist})
    else:
        return redirect(LoginPage)

def filteruserdcardpaymentreport(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = datefilterform(request.POST or None)
            print(form.errors)
            if form.is_valid():
                currentuser=request.session["user"]
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                userdet=UserData.objects.get(username=currentuser)
                phist = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdet).order_by('-date')
                return render(request,"user/dcard/paymentReport.html",{'form':datefilterform,'user':userdet,'phist':phist})
            else:
                return redirect(userdcardpaymentreport)
        else:
            return redirect(userdcardpaymentreport)
    else:
        return redirect(LoginPage)

def userrcardpaymentreport(request):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=request.session["user"])
        phist = fundTransactionReport.objects.filter(destination=userdet).order_by('-date')
        return render(request,"user/rcard/paymentReport.html",{'form':datefilterform,'user':userdet,'phist':phist})
    else:
        return redirect(LoginPage)

def filteruserrcardpaymentreport(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = datefilterform(request.POST or None)
            print(form.errors)
            if form.is_valid():
                currentuser=request.session["user"]
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                userdet=UserData.objects.get(username=currentuser)
                phist = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdet).order_by('-date')
                return render(request,"user/rcard/paymentReport.html",{'form':datefilterform,'user':userdet,'phist':phist})
            else:
                return redirect(userrcardpaymentreport)
        else:
            return redirect(userrcardpaymentreport)
    else:
        return redirect(LoginPage)


#_________________________________________________________________________________API__________________________________________________________________________

#def voiplogin(request):

class UserLogin(APIView):
    def get(self, request):
        username = request.GET['username']
        password = request.GET['password']
        print(username)
        print(password)
        return Response(status=status.HTTP_302_FOUND)
        #pass;

    def post(self,request):
        """
        User Authentication Api.\n
        Arguments :\n
        username - String
        password - String
        """
        username = request.POST['username']
        password = request.POST['password']
        print(username)
        print(password)
        hashkey = username+password
        hash = hashlib.sha256(hashkey.encode()).hexdigest()
        if (UserData.objects.filter(username = username, password = hash)).exists():
            user = UserData.objects.get(username = username, password = hash)
            userdata=UserDataSerializer(user,many=True)
            return Response(userdata.data,status=status.HTTP_302_FOUND)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

login_schema = AutoSchema(manual_fields=[
    coreapi.Field("username", required=True, location="form", type="string", description="username"),
])

@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@schema(login_schema)
def apiLogin(request):
    username = request.data.get("username")
    try:
        user = UserData.objects.get(username=username)
        print(user.status)
        if(user):
            if(user.status):
                userdata=UserDataSerializer(user)
                return Response({'success':True,'data':userdata.data}, status=HTTP_200_OK)
            else:
                return Response({'success': False,'message':'Login Restricted By Parent'}, status=HTTP_200_OK)
        else:
            return Response({'success': False, 'message':'Invalid Credentials'},status=HTTP_200_OK)
    except:
        return Response({'success': False, 'message':'Invalid Credentials'},status=HTTP_200_OK)


resellerlist_schema = AutoSchema(manual_fields=[
    coreapi.Field("username", required=True, location="form", type="string", description="username"),
    coreapi.Field("password", required=True, location="form", type="string", description="password"),
])
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@schema(resellerlist_schema)
def apiGetAllResellerList(request):
    """
    <h3 style="color:green;">Get All Reseller List Under A User.</h3>

    """
    username = request.data.get("username")
    user = UserData.objects.get(username=username)
    if(user.postId=="Admin"):
        resellers = UserData.objects.filter(sponserId=user,postId="Reseller")
        if(resellers):
            users = ResellerOrUserListSerializer(resellers,many=True)
            return Response({'success':True, 'data':users.data},status=HTTP_200_OK)
        else:
            return Response({'success':True, 'data':[]},status=HTTP_200_OK)
    elif(user.postId=="Reseller"):
        resellers = UserData.objects.filter(sponserId=username,postId="Sub_Reseller")
        if(resellers):
            users = ResellerOrUserListSerializer(resellers,many=True)
            return Response({'success':True,'data':users.data},status=HTTP_200_OK)
        else:
            return Response({'success':True,'data':[]},status=HTTP_200_OK)
    else:
        return Response({'success':'False','message':'Error Occured'},status=HTTP_200_OK)

userlist_schema = AutoSchema(manual_fields=[
    coreapi.Field("username", required=True, location="form", type="string", description="username"),
    coreapi.Field("password", required=True, location="form", type="string", description="password"),
])
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@schema(userlist_schema)
def apiGetAllUserList(request):
    try:
        username = request.data.get("username")
        user = UserData.objects.get(username=username)
        users = UserData.objects.filter(sponserId=user)
        if(users):
            userdata = ResellerOrUserListSerializer(users,many=True)
            return Response({'success':True,'data':userdata.data},status=HTTP_200_OK)
        else:
            return Response({'success':True,'data':[]},status=HTTP_200_OK)
    except:
        return Response({'success':False,'message':'Something Unexpected Occurred'},status=HTTP_200_OK)

getsingleuser_schema = AutoSchema(manual_fields=[
    coreapi.Field("username", required=True, location="form", type="string", description="username"),
    coreapi.Field("password", required=True, location="form", type="string", description="password"),
    coreapi.Field("user", required=True, location="form", type="string", description="user"),
])
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@schema(getsingleuser_schema)
def apiGetSingleUserDetails(request):
    try:
       username = request.data.get("user")
       user = UserData.objects.get(username=username)
       userdata = SingleUserDetailsSerializer(user)
       return Response({'success':True,'data':userdata.data},status=HTTP_200_OK)
    except:
        return Response({'success':False,'message':'Invalid User'},status=HTTP_200_OK)

balancetransfer_schema = AutoSchema(manual_fields=[
    coreapi.Field("username", required=True, location="form", type="string", description="username"),
    coreapi.Field("password", required=True, location="form", type="string", description="password"),
    coreapi.Field("user", required=True, location="form", type="string", description="username"),
    coreapi.Field("amount", required=True, location="form", type="string", description="password"),
])
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@schema(balancetransfer_schema)
def apiBalanceTransfer(request):
    username = request.data.get("username")
    sponser = request.data.get("user")
    amount = request.data.get("amount")
    try:
        sponserdet = UserData.objects.get(username=sponser)
        bal = sponserdet.balance
        newbal=bal+Decimal(amount)
        cdbal = sponserdet.targetAmt
        newcdbal = cdbal-Decimal(amount)
        sponserdet.targetAmt = newcdbal
        sponserdet.balance = newbal
        sponserdet.save()
        userdetails = UserData.objects.get(username=username)
        btreport = balanceTransactionReport()
        btreport.source = userdetails
        btreport.destination = sponserdet
        btreport.category = "BT"
        btreport.amount = amount
        btreport.pbalance = bal
        btreport.nbalance = newbal
        btreport.cramount = newcdbal
        btreport.remarks = 'Added To Balance'
        btreport.save()
        data={'balance':newbal,'credit':newcdbal}
        return Response({'success':True,'data':data},status=HTTP_200_OK)
    except:
        return Response({'success':False,'message':'Something Unexpected Occurred'},status=HTTP_200_OK)


fundtransfer_schema = AutoSchema(manual_fields=[
    coreapi.Field("username", required=True, location="form", type="string", description="username"),
    coreapi.Field("password", required=True, location="form", type="string", description="password"),
    coreapi.Field("user", required=True, location="form", type="string", description="sponser"),
    coreapi.Field("amount", required=True, location="form", type="string", description="amount"),
    coreapi.Field("remarks", required=True, location="form", type="string", description="remarks"),
])
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@schema(fundtransfer_schema)
def apiFundTransfer(request):
    username = request.data.get("username")
    sponser = request.data.get("user")
    amount = request.data.get("amount")
    remarks = request.data.get("remarks")
    try:
        sponserdet = UserData.objects.get(username=sponser)
        print(sponserdet.username)
        obalance = sponserdet.targetAmt
        print(obalance)
        cdbal = sponserdet.targetAmt
        newcdbal = cdbal+Decimal(amount)
        sponserdet.targetAmt = newcdbal
        sponserdet.save()
        closeuser = UserData.objects.get(username=sponser)
        print(closeuser)
        userdetails = UserData.objects.get(username=username)
        print(userdetails)
        ftreport=fundTransactionReport()
        ftreport.source = userdetails
        ftreport.destination = sponserdet
        ftreport.obalance = obalance
        ftreport.cbalance = closeuser.targetAmt
        ftreport.role = sponserdet.postId
        ftreport.amount = amount
        ftreport.balance = newcdbal
        ftreport.remarks = remarks
        ftreport.save()
        data={'credit':newcdbal}
        return Response({'success':True,'data':data},status=HTTP_200_OK)
    except:
        return Response({'success':False,'message':'Something Unexpected Occurred'},status=HTTP_200_OK)

changepassword_schema = AutoSchema(manual_fields=[
    coreapi.Field("username", required=True, location="form", type="string", description="username"),
    coreapi.Field("password", required=True, location="form", type="string", description="password"),
    coreapi.Field("cpassword", required=True, location="form", type="string", description="cpassword"),
    coreapi.Field("npassword", required=True, location="form", type="string", description="npassword"),
])
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@schema(changepassword_schema)
def apiChangePassword(request):
    username = request.data.get("username")
    cpassword = request.data.get("cpassword")
    npassword = request.data.get("npassword")
    hashkey = username+cpassword
    hash = hashlib.sha256(hashkey.encode()).hexdigest()
    if (UserData.objects.filter(username = username, password = hash)).exists():
        user = UserData.objects.get(username = username, password = hash)
        newhashkey = username+npassword
        newhash = hashlib.sha256(newhashkey.encode()).hexdigest()
        user.password=newhash
        user.save()
        return Response({'success':True,'data':'Password Changed Successfully'}, status=HTTP_200_OK)
    else:
        return Response({'success':False,'message':'Something Unexpected Occurred'},status=HTTP_200_OK)

resetpassword_schema = AutoSchema(manual_fields=[
    coreapi.Field("username", required=True, location="form", type="string", description="username"),
    coreapi.Field("password", required=True, location="form", type="string", description="password"),
    coreapi.Field("user", required=True, location="form", type="string", description="user"),
])
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@schema(resetpassword_schema)
def apiResetPassword(request):
    username = request.data.get("user")
    try:
        userdet= UserData.objects.get(username=username)
        if(userdet):
            password = username
            hashkey = username+password
            newhash = hashlib.sha256(hashkey.encode()).hexdigest()
            userdet.password=newhash
            userdet.save()
            return Response({'success':True,'data':'Successfully Reseted'},status=HTTP_200_OK)
        else:
            return Response({'success':False,'message':'Something Unexpected Occurred'},status=HTTP_200_OK)
    except:
        return Response({'success':False,'message':'Something Unexpected Occurred'},status=HTTP_200_OK)

balancetransactionreport_schema = AutoSchema(manual_fields=[
    coreapi.Field("username", required=True, location="form", type="string", description="username"),
    coreapi.Field("password", required=True, location="form", type="string", description="password"),
])
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@schema(balancetransactionreport_schema)
def apiGetBalanceTransactionHistory(request):
    username = request.data.get("username")
    userdetails = UserData.objects.get(username=username)
    try:
        bthist = balanceTransactionReport.objects.filter(source=userdetails,category="BT").order_by('-date')[:40]
        if(bthist):
            data = BalanceTransferHistorySerializer(bthist,many=True)
            return Response({'success':True,'data':data.data},status=HTTP_200_OK)
        else:
            return Response({'success':True,'data':[]},status=HTTP_200_OK)
    except:
        return Response({'success':False,'message':'Something Unexpected Occurred'},status=HTTP_200_OK)

fundtransactionreport_schema = AutoSchema(manual_fields=[
    coreapi.Field("username", required=True, location="form", type="string", description="username"),
    coreapi.Field("password", required=True, location="form", type="string", description="password"),
])
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@schema(fundtransactionreport_schema)
def apiGetFundTransactionHistory(request):
    username = request.data.get("username")
    userdetails = UserData.objects.get(username=username)
    try:
        bthist = fundTransactionReport.objects.filter(source=userdetails).order_by('-date')[:40]
        #print(balhist)
        if(bthist):
            data = FundTransferHistorySerializer(bthist,many=True)
            return Response({'success':True,'data':data.data},status=HTTP_200_OK)
        else:
            return Response({'success':True,'data':[]},status=HTTP_200_OK)
    except:
        return Response({'success':False,'message':'Something Unexpected Occurred'},status=HTTP_200_OK)

creditbalance_schema = AutoSchema(manual_fields=[
    coreapi.Field("username", required=True, location="form", type="string", description="username"),
    coreapi.Field("password", required=True, location="form", type="string", description="password"),
    coreapi.Field("user", required=True, location="form", type="string", description="user"),
])
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@schema(creditbalance_schema)
def apiGetCreditBalance(request):
    username = request.data.get("user")
    try:
        userdetails = UserData.objects.get(username=username)
        if(userdetails):
            data={'credit':userdetails.targetAmt}
            return Response({'success':True,'data':data},status=HTTP_200_OK)
        else:
            return Response({'success':True,'data':[]},status=HTTP_200_OK)
    except:
        return Response({'success':False,'message':'Something Unexpected Occurred'},status=HTTP_200_OK)

voipstore_schema = AutoSchema(manual_fields=[
    coreapi.Field("username", required=True, location="form", type="string", description="username"),
    coreapi.Field("password", required=True, location="form", type="string", description="password"),
])
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@schema(voipstore_schema)
def apiGetVoipStore(request):
    username = request.data.get("username")
    userdet = UserData.objects.get(username=username)
    if(userdet.postId != "Admin"):
        pdcts = vcloudAssignments.objects.filter(assignedto=username,brand__category="card with cutting").order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description','margin')
        if(len(pdcts)==0):
            return Response(status=HTTP_204_NO_CONTENT)
        else:
            data=dict()
            content = []
            for i in pdcts:
                try:
                    pd=vcloudProducts.objects.filter(brand__id=i['brand__id'], status=True).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
                    lpd=list(pd)
                    count=0
                    if not lpd:
                        pass
                    else:
                        username = request.data.get("username")
                        productcost=Decimal(lpd[0]['brand__denomination'])
                        while(True):
                            userdet2=UserData.objects.filter(username=username).values('sponserId','postId')
                            margindet=vcloudAssignments.objects.filter(assignedto=username,brand__brand=i['brand__brand']).values('margin')
                            if(userdet2[0]['postId']=="Admin"):
                                break;
                            else:
                                productcost = Decimal(productcost)+Decimal(margindet[0]['margin'])
                                username=userdet2[0]['sponserId']
                            count=int(count)+1
                        data={"brand__id":lpd[0]['brand__id'],"brand__brand":lpd[0]['brand__brand'],'count':lpd[0]['productcount'],'brand__logo':lpd[0]['brand__logo'],'cost':productcost,'brand__currency':lpd[0]['brand__currency'],'brand__description':lpd[0]['brand__description']}
                        content.append(data)
                except Exception as e:
                    print(e)
                    pass
            return Response(content,status=HTTP_200_OK)
    else:
        return Response(status=HTTP_406_NOT_ACCEPTABLE)

filteredvoipstore_schema = AutoSchema(manual_fields=[
    coreapi.Field("username", required=True, location="form", type="string", description="username"),
    coreapi.Field("password", required=True, location="form", type="string", description="password"),
    coreapi.Field("category", required=True, location="form", type="string", description="category"),
])
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@schema(filteredvoipstore_schema)
def apiGetFilteredVoipStore(request):
    username = request.data.get("username")
    category = request.data.get("category")
    userdet = UserData.objects.get(username=username)
    try:
        if(userdet.postId!="Admin"):
            if(category=="Cutting"):
                pdcts = vcloudAssignments.objects.filter(assignedto=username,brand__category="card with cutting").order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
                print(pdcts)
                if(len(pdcts)==0):
                    return Response({'success':True,'data':[]},status=HTTP_200_OK)
                else:
                    data=dict()
                    content = []
                    for i in pdcts:
                        try:
                            pd=vcloudProducts.objects.filter(brand=i['brand__id'],status=True).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
                            lpd=list(pd)
                            count=0
                            if not lpd:
                                pass;
                            else:
                                username = request.data.get("username")
                                productcost=Decimal(lpd[0]['brand__denomination'])
                                while(True):
                                    userdet2=UserData.objects.filter(username=username).values('sponserId','postId')
                                    margindet=vcloudAssignments.objects.filter(assignedto=username,brand__brand=i['brand__brand']).values('margin')
                                    if(userdet2[0]['postId']=="Admin"):
                                        break;
                                    else:
                                        productcost = Decimal(productcost)+Decimal(margindet[0]['margin'])
                                        username=userdet2[0]['sponserId']
                                    count=int(count)+1
                                data={"brand__id":lpd[0]['brand__id'],"brand__brand":lpd[0]['brand__brand'],'count':lpd[0]['productcount'],'brand__logo':lpd[0]['brand__logo'],'cost':productcost,'brand__currency':lpd[0]['brand__currency'],'brand__description':lpd[0]['brand__description']}
                                content.append(data)
                        except Exception as e:
                            print(e)
                            pass
                    return Response({'success':True,'data':content},status=HTTP_200_OK)
            else:
                print(username)
                pdcts = vcloudAssignments.objects.filter(assignedto=username,brand__category="card without cutting").order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
                print(pdcts)
                if(len(pdcts)==0):
                    return Response({'success':True,'data':[]},status=HTTP_200_OK)
                else:
                    data=dict()
                    content = []
                    for i in pdcts:
                        try:
                            pd=vcloudProducts.objects.filter(brand=i['brand__id'],status=True).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand', 'productcount','brand__id','brand__logo','brand__denomination','brand__currency','brand__description')
                            lpd=list(pd)
                            count=0
                            if not lpd:
                                pass
                            else:
                                username = request.data.get("username")
                                productcost=Decimal(lpd[0]['brand__denomination'])
                                while(True):
                                    userdet2=UserData.objects.filter(username=username).values('sponserId','postId')
                                    margindet=vcloudAssignments.objects.filter(assignedto=username,brand__brand=i['brand__brand']).values('margin')
                                    if(userdet2[0]['postId']=="Admin"):
                                        break;
                                    else:
                                        productcost = Decimal(productcost)+Decimal(margindet[0]['margin'])
                                        username=userdet2[0]['sponserId']
                                    count=int(count)+1
                                data={"brand__id":lpd[0]['brand__id'],"brand__brand":lpd[0]['brand__brand'],'count':lpd[0]['productcount'],'brand__logo':lpd[0]['brand__logo'],'cost':productcost,'brand__currency':lpd[0]['brand__currency'],'brand__description':lpd[0]['brand__description']}
                                content.append(data)
                        except Exception as e:
                            pass;
                    return Response({'success':True, 'data':content},status=HTTP_200_OK)
        else:
            return Response({'success':False,'message':'Restricted UserType'},status=HTTP_200_OK)
    except:
        return Response({'success':False,'message':'Something Unexpected Occurred'},status=HTTP_200_OK)

getownbrand_schema = AutoSchema(manual_fields=[
    coreapi.Field("username", required=True, location="form", type="string", description="username"),
    coreapi.Field("password", required=True, location="form", type="string", description="password"),
])
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@schema(getownbrand_schema)
def apiGetOwnBrandList(request):
    username = request.data.get("username")
    userdet = UserData.objects.get(username=username)
    if(userdet.postId!="Admin"):
        pdcts = vcloudAssignments.objects.filter(assignedto=username).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand','brand__id','brand__logo','brand__currency','brand__description')
        return Response({'success':True,'data':pdcts},status=HTTP_200_OK)
    else:
        return Response({'success':False,'message':'Something Unexpected Occurred'},status=HTTP_200_OK)

getpurchase_schema = AutoSchema(manual_fields=[
    coreapi.Field("username", required=True, location="form", type="string", description="username"),
    coreapi.Field("password", required=True, location="form", type="string", description="password"),
    coreapi.Field("brand", required=True, location="form", type="string", description="brand"),
    coreapi.Field("quantity", required=True, location="form", type="string", description="quantity"),
    coreapi.Field("amount", required=True, location="form", type="string", description="amount"),
])
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@schema(getpurchase_schema)
def apiGetPurchase(request):
    try:
        username = request.data.get("username")
        brand = request.data.get("brand")
        quantity = request.data.get("quantity")
        amt = request.data.get("amount")
        branddet=vcloudBrands.objects.get(brand=brand)
        userdet=UserData.objects.get(username=username)
        strlog = username+' buyed '+quantity+' '+brand
        #str = username+' Buyed '+str(quantity)+' '+brand+' by '+amount
        print(strlog)
        plog=PurchaseLog()
        plog.logdesc=strlog
        plog.save()
        print("Hello")
        ctime=datetime.now()
        time = timedelta(minutes = 5)
        now_minus_5 = ctime - time
        checkqty=vcloudProducts.objects.filter(Q(brand__brand=brand) & Q(status=True) & (Q(sdate__isnull=True) | Q(sdate__lte=now_minus_5))).values('brand').annotate(productcount=Count('brand')).values('productcount')
        print(checkqty)
        needamt=0;
        result=list()
        licheckqty=list(checkqty)
        brand_id=0
        deno=0
        print(licheckqty[0]['productcount'])
        if(licheckqty[0]['productcount'] >= int(quantity)):
            print("Haiii")
            usertype=''
            marginlist=list()
            margins=0
            count=0;
            flag=True
            prdct_id=''
            mllist=list()
            sponserlist=list()
            prdctdet = vcloudProducts.objects.filter(Q(brand__brand=brand) & Q(status=True) & (Q(sdate__isnull=True) | Q(sdate__lte=now_minus_5)))[:int(quantity)]
            ctime = datetime.now()
            for i in prdctdet:
                i.productstatus=1
                i.suser = userdet
                i.sdate = ctime
                i.save()
            count=0
            admin=''
            while(True):
                userdet2=UserData.objects.filter(username=username).values('sponserId','postId','balance')
                margindet=vcloudAssignments.objects.filter(assignedto=username,brand__brand=brand).values('margin')
                if(userdet2[0]['postId']=="Admin"):
                    admin=username
                    break;
                else:
                    cost=Decimal(amt)
                    prdctcost = (cost*Decimal(quantity))-(Decimal(margins)*Decimal(quantity))
                    margins=margins+Decimal(margindet[0]['margin'])
                    if(userdet2[0]['balance']>=prdctcost):
                        data={'margin':margindet[0]['margin'],'balance':userdet2[0]['balance'],'username':username,'prdctcost':prdctcost}
                        marginlist.append(data)
                        mllist.append(margindet[0]['margin'])
                        sponserlist.append(username)
                    else:
                        flag=False
                        break;
                username=userdet2[0]['sponserId']
            print(flag)
            if(flag):
                try:
                    prdctcddet=vcloudProducts.objects.filter(brand__brand=brand,status=True,productstatus=1,suser=userdet,sdate=ctime)[:int(quantity)]
                    for h in prdctcddet:
                        h.status=False
                        h.save()
                        #print(h.username)
                        brand_id=h.brand.id
                        deno=h.brand.denomination
                        prdct_id=prdct_id+""+str(h.id)+","
                        res={"productid":h.id,"carduname":h.username,'password':h.password,'brand':h.brand.brand,'brand_logo':h.brand.logo.url,'status':h.status,'suser':username,'sdate':convert_datetime_timezone(h.sdate),'description':branddet.description,'denomination':amt}
                        result.append(res)
                    ml=marginlist[::-1]
                    for k in ml:
                        uname = k['username']
                        margin = k['margin']
                        balance = k['balance']
                        pcost = k['prdctcost']
                        cb=Decimal(balance)-Decimal(pcost)
                        userd=UserData.objects.get(username=uname)
                        userd.balance=cb
                        userd.save()
                    mllen = len(mllist)
                    username = request.data.get("username")
                    closeuser = UserData.objects.get(username=username)
                    vcrep=vcloudtransactions()
                    vcrep.saleduser = userdet
                    vcrep.brand = brand
                    vcrep.type = "Vcloud"
                    vcrep.brand_id = brand_id
                    vcrep.product_id = prdct_id
                    vcrep.obalance = userdet.balance
                    vcrep.quantity = quantity
                    vcrep.cbalance = closeuser.balance
                    vcrep.amount = amt
                    vcrep.rtype = "App"
                    vcrep.denominations = deno
                    ms = mllist[::-1]
                    mu = sponserlist[::-1]
                    ad=UserData.objects.get(username=admin)
                    if(mllen==1):
                        vcrep.margin1=ms[0]
                        vcrep.sponser1=ad
                        vcrep.sponser2=UserData.objects.get(username=sponserlist[0])
                    elif(mllen==2):
                        vcrep.margin1=ms[0]
                        vcrep.margin2=ms[1]
                        vcrep.sponser1=ad
                        vcrep.sponser2=UserData.objects.get(username=sponserlist[1])
                        vcrep.sponser3=UserData.objects.get(username=sponserlist[0])
                    else:
                        vcrep.margin1=ms[0]
                        vcrep.margin2=ms[1]
                        vcrep.margin3=ms[2]
                        vcrep.sponser1=ad
                        vcrep.sponser2=UserData.objects.get(username=sponserlist[2])
                        vcrep.sponser3=UserData.objects.get(username=sponserlist[1])
                        vcrep.sponser4=UserData.objects.get(username=sponserlist[0])
                    vcrep.save()
                    return Response({'success':True,'data':result},status=HTTP_200_OK)
                except:
                    return Response({'success':False,'message':'Sorry You Requested Product is buyed by Someone'},status=HTTP_200_OK)
            else:
                return Response({'success':False,'message':'Something Wrong May Happend, Try Again.! Else Contact Your Administrator'},status=HTTP_200_OK)

    except:
        return Response({'success':False,'message':'Something Unexpected Occured'},status=HTTP_200_OK)

getpurchasereport_schema = AutoSchema(manual_fields=[
    coreapi.Field("username", required=True, location="form", type="string", description="username"),
    coreapi.Field("password", required=True, location="form", type="string", description="password"),
])
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@schema(getpurchasereport_schema)
def apiGetPurchaseReport(request):
    try:
        username = request.data.get("username")
        print(username)
        content=list()
        noofrecords=0
        productsum =0
        quantitysum =0
        profitsum =0
        count=0
        userdet = UserData.objects.get(username=username)
        print(userdet)
        if(userdet.postId=='Reseller'):
            #print("Haiii")
            vcloudtxns=vcloudtransactions.objects.filter(sponser2__username=username,type="Vcloud",rtype="App").order_by('-date')[:20]
            print(vcloudtxns)
            for i in vcloudtxns:
                print(i)
                cost=i.denominations+i.margin1
                productsum=productsum+(cost*i.quantity)
                quantitysum=quantitysum+i.quantity
                print(i)
                if(i.saleduser.username==username):
                    profit=0
                    data={"id":i.id,"saleduser":i.sponser2.name,"role":i.sponser2.postId,"date":convert_datetime_timezone(i.date),"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"denomination":i.denominations,"margin":0,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit}
                    content.append(data)
                    profitsum = profitsum+profit
                    count=count+1
                    print(data)
                else:
                    profit=i.margin2
                    data={"id":i.id,"saleduser":i.sponser3.name,"role":i.sponser3.postId,"date":convert_datetime_timezone(i.date),"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"denomination":i.denominations,"margin":i.margin2,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit}
                    content.append(data)
                    profitsum = profitsum+profit
                    count=count+1
                #print(content)
        elif(userdet.postId=='Sub_Reseller'):
            vcloudtxns=vcloudtransactions.objects.filter(sponser3__username=username,type="Vcloud",rtype="App").order_by('-date')[:20]
            for i in vcloudtxns:
                cost=i.denominations+i.margin1+i.margin2
                productsum=productsum+(cost*i.quantity)
                quantitysum=quantitysum+i.quantity
                if(i.saleduser.username==username):
                    profit=0
                    data={"id":i.id,"saleduser":i.sponser3.name,"role":i.sponser3.postId,"date":convert_datetime_timezone(i.date),"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"denomination":i.denominations,"margin":0,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit}
                    content.append(data)
                    profitsum = profitsum+profit
                else:
                    profit=i.margin3
                    data={"id":i.id,"saleduser":i.sponser4.name,"role":i.sponser4.postId,"date":convert_datetime_timezone(i.date),"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"denomination":i.denominations,"margin":i.margin3,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit}
                    content.append(data)
                    profitsum = profitsum+profit
        else:
            vcloudtxns=vcloudtransactions.objects.filter(saleduser__username=username,type="Vcloud",rtype="App").order_by('-date')[:20]
            for i in vcloudtxns:
                data={"id":i.id,"saleduser":i.saleduser.name,"role":i.saleduser.postId,"date":convert_datetime_timezone(i.date),"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"denomination":i.denominations,"margin":0,"quantity":i.quantity,"amount":(i.amount*i.quantity),"profit":0}
                content.append(data)
                productsum=productsum+(i.amount*i.quantity)
                quantitysum=quantitysum+i.quantity
                profitsum = 0
        print(content)
        if(len(content)==0):
            return Response({'success':True,'data':[]},status=HTTP_200_OK)
        else:
            data={"transaction":content,'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum}
            return Response({'success':True,'data':data},status=HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({'success':False,'message':'Something Unexpected Occured'},status=HTTP_200_OK)

getpurchaseproductreport_schema = AutoSchema(manual_fields=[
    coreapi.Field("username", required=True, location="form", type="string", description="Username"),
    coreapi.Field("password", required=True, location="form", type="string", description="Password"),
    coreapi.Field("id", required=True, location="form", type="string", description="Transaction Id"),
    coreapi.Field("type", required=True, location="form", type="string", description="Transaction Type")
])
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@schema(getpurchaseproductreport_schema)
def apiGetPurchasedProductReport(request):
    try:
        id = request.data.get("id")
        type = request.data.get("type")
        pdlist=list()
        vcloudtxns=vcloudtransactions.objects.get(id=id)
        productid=vcloudtxns.product_id
        result = productid.rstrip(',')
        pdid = result.split(',')
        if(type=="Vcloud"):
            for i in pdid:
                pddet=vcloudProducts.objects.get(id=i)
                data={"id":pddet.id,"brand":pddet.brand.brand,"carduname":pddet.username,"password":pddet.password,"denomination":vcloudtxns.denominations,"brand_logo":pddet.brand.logo.url,"sdate":pddet.sdate,"description":pddet.brand.description}
                pdlist.append(data)
        elif(type=="Dcard"):
            for i in pdid:
                pddet=datacardproducts.objects.get(id=i)
                data={"id":pddet.id,"brand":pddet.brand.brand,"carduname":pddet.username,"denomination":vcloudtxns.denominations,"brand_logo":pddet.brand.logo.url,"sdate":pddet.sdate,"description":pddet.brand.description}
                pdlist.append(data)
        else:
            for i in pdid:
                pddet=rcardProducts.objects.get(id=i)
                data={"id":pddet.id,"brand":pddet.brand.brand,"carduname":pddet.username,"denomination":vcloudtxns.denominations,"brand_logo":pddet.brand.logo.url,"sdate":pddet.sdate,"description":pddet.brand.description}
                pdlist.append(data)
        return Response({'success':True,'data':pdlist},status=HTTP_200_OK)
    except:
        return Response({'success':False,'message':'Something Unexpected Occurred'},status=HTTP_200_OK)

filteredtransactionreport_schema = AutoSchema(manual_fields=[
    coreapi.Field("username", required=True, location="form", type="string", description="username"),
    coreapi.Field("password", required=True, location="form", type="string", description="password"),
    coreapi.Field("fromdate", required=True, location="form", type="date", description="transaction id"),
    coreapi.Field("todate", required=True, location="form", type="date", description="transaction id"),
    coreapi.Field("user", required=True, location="form", type="date", description="transaction id"),
    coreapi.Field("type", required=True, location="form", type="date", description="transaction id"),
])
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@schema(filteredtransactionreport_schema)
def apiGetFilteredTransactionReport(request):
    username=request.data.get("username")
    fromdate=request.data.get("fromdate")
    todate=request.data.get("todate")
    fusername=request.data.get("user")
    type=request.data.get("type")
    content=list()
    noofrecords=0
    productsum =0
    quantitysum =0
    profitsum =0
    userdet = UserData.objects.get(username=fusername)
    #vcloudtxns=vcloudtransactions.objects.filter(date__lte=todate,date__gte=fromdate).order_by('-date')
    #print(vcloudtxns)
    try:
        userdet = UserData.objects.get(username=username)
        print(userdet.postId)
        if(userdet.postId=='Reseller'):
            vcloudtxns=vcloudtransactions.objects.filter(sponser2__username=username,date__gte=fromdate,date__lte=todate,type=type,rtype="App").order_by('-date')
            print(vcloudtxns)
            for i in vcloudtxns:
                print(i)
                cost=i.denominations+i.margin1
                productsum=productsum+(cost*i.quantity)
                quantitysum=quantitysum+i.quantity
                print(i)
                if(i.saleduser.username==username):
                    profit=0
                    data={"id":i.id,"saleduser":i.sponser2.name,"role":i.sponser2.postId,"date":convert_datetime_timezone(i.date),"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"denomination":i.denominations,"margin":0,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit}
                    content.append(data)
                    profitsum = profitsum+profit
                    print(data)
                else:
                    profit=i.margin2
                    data={"id":i.id,"saleduser":i.sponser3.name,"role":i.sponser3.postId,"date":convert_datetime_timezone(i.date),"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"denomination":i.denominations,"margin":i.margin2,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit}
                    content.append(data)
                    profitsum = profitsum+profit
                #print(content)
        elif(userdet.postId=='Sub_Reseller'):
            vcloudtxns=vcloudtransactions.objects.filter(sponser3__username=username,date__lte=todate,date__gte=fromdate,type=type,rtype="App").order_by('-date')
            for i in vcloudtxns:
                cost=i.denominations+i.margin1+i.margin2
                productsum=productsum+(cost*i.quantity)
                quantitysum=quantitysum+i.quantity
                if(i.saleduser.username==username):
                    profit=0
                    data={"id":i.id,"saleduser":i.sponser3.name,"role":i.sponser3.postId,"date":convert_datetime_timezone(i.date),"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"denomination":i.denominations,"margin":0,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit}
                    content.append(data)
                    profitsum = profitsum+profit
                else:
                    profit=i.margin3
                    data={"id":i.id,"saleduser":i.sponser4.name,"role":i.sponser4.postId,"date":convert_datetime_timezone(i.date),"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"denomination":i.denominations,"margin":i.margin3,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit}
                    content.append(data)
                    profitsum = profitsum+profit
        else:
            vcloudtxns=vcloudtransactions.objects.filter(saleduser__username=username,date__lte=todate,date__gte=fromdate,type=type,rtype="App").order_by('-date')
            for i in vcloudtxns:
                data={"id":i.id,"saleduser":i.saleduser.name,"role":i.saleduser.postId,"date":convert_datetime_timezone(i.date),"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"denomination":i.denominations,"margin":0,"quantity":i.quantity,"amount":(i.amount*i.quantity),"profit":0}
                content.append(data)
                productsum=productsum+(i.amount*i.quantity)
                quantitysum=quantitysum+i.quantity
                profitsum = 0
        print(content)
        if(len(content)==0):
            return Response({'success':True,'data':[]},status=HTTP_200_OK)
        else:
            data={"transaction":content,'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum}
            return Response({'success':True,'data':data},status=HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({'success':False,'message':'Something Unexpected Occured'},status=HTTP_200_OK)

filteredbalancetransactionreport_schema = AutoSchema(manual_fields=[
    coreapi.Field("username", required=True, location="form", type="string", description="username"),
    coreapi.Field("password", required=True, location="form", type="string", description="password"),
    coreapi.Field("fromdate", required=True, location="form", type="date", description="fromdate"),
    coreapi.Field("todate", required=True, location="form", type="date", description="todate"),
])
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@schema(filteredbalancetransactionreport_schema)
def apiGetFilteredBalanceTransactionHistory(request):
    username = request.data.get("username")
    userdetails = UserData.objects.get(username=username)
    fromdate=request.data.get("fromdate")
    todate=request.data.get("todate")
    try:
        bthist = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails)
        if(bthist):
            data = BalanceTransferHistorySerializer(bthist,many=True)
            return Response({'success':True,'data':data.data},status=HTTP_200_OK)
        else:
            return Response({'success':True,'data':[]},status=HTTP_200_OK)
    except:
        return Response({'success':False,'message':'Something Unexpected Occured'},status=HTTP_200_OK)

filteredtobalancetransactionreport_schema = AutoSchema(manual_fields=[
    coreapi.Field("username", required=True, location="form", type="string", description="username"),
    coreapi.Field("password", required=True, location="form", type="string", description="password"),
    coreapi.Field("fromdate", required=True, location="form", type="date", description="fromdate"),
    coreapi.Field("todate", required=True, location="form", type="date", description="todate"),
])
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@schema(filteredtobalancetransactionreport_schema)
def apiGetFilteredToBalanceTransactionHistory(request):
    username = request.data.get("username")
    userdetails = UserData.objects.get(username=username)
    fromdate=request.data.get("fromdate")
    todate=request.data.get("todate")
    try:
        bthist = balanceTransactionReport.objects.filter(date__gte =fromdate,date__lte=todate, destination=userdetails)
        if(bthist):
            data = BalanceTransferHistorySerializer(bthist,many=True)
            return Response({'success':True,'data':data.data},status=HTTP_200_OK)
        else:
            return Response({'success':True,'data':[]},status=HTTP_200_OK)
    except:
        return Response({'success':False,'message':'Something Unexpected Occured'},status=HTTP_200_OK)

filteredfundtransactionreport_schema = AutoSchema(manual_fields=[
    coreapi.Field("username", required=True, location="form", type="string", description="username"),
    coreapi.Field("password", required=True, location="form", type="string", description="password"),
    coreapi.Field("fromdate", required=True, location="form", type="date", description="fromdate"),
    coreapi.Field("todate", required=True, location="form", type="date", description="todate"),
])
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@schema(filteredfundtransactionreport_schema)
def apiGetFilteredFundTransactionHistory(request):
    username = request.data.get("username")
    userdetails = UserData.objects.get(username=username)
    fromdate=request.data.get("fromdate")
    todate=request.data.get("todate")
    try:
        bthist = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,source=userdetails)
        if(bthist):
            data = FundTransferHistorySerializer(bthist,many=True)
            return Response({'success':True,'data':data.data},status=HTTP_200_OK)
        else:
            return Response({'success':True,'data':[]},status=HTTP_200_OK)
    except:
        return Response({'success':False,'message':'Something Unexpected Occured'},status=HTTP_200_OK)

filteredtofundtransactionreport_schema = AutoSchema(manual_fields=[
    coreapi.Field("username", required=True, location="form", type="string", description="username"),
    coreapi.Field("password", required=True, location="form", type="string", description="password"),
    coreapi.Field("fromdate", required=True, location="form", type="date", description="fromdate"),
    coreapi.Field("todate", required=True, location="form", type="date", description="todate"),
])
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@schema(filteredtofundtransactionreport_schema)
def apiGetFilteredToFundTransactionHistory(request):
    username = request.data.get("username")
    userdetails = UserData.objects.get(username=username)
    fromdate=request.data.get("fromdate")
    todate=request.data.get("todate")
    try:
        bthist = fundTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdetails)
        if(bthist):
            data = FundTransferHistorySerializer(bthist,many=True)
            return Response({'success':True,'data':data.data},status=HTTP_200_OK)
        else:
            return Response({'success':True,'data':[]},status=HTTP_200_OK)
    except:
        return Response({'success':False,'message':'Something Unexpected Occured'},status=HTTP_200_OK)

tobalncetransactionreport_schema = AutoSchema(manual_fields=[
    coreapi.Field("username", required=True, location="form", type="string", description="username"),
    coreapi.Field("password", required=True, location="form", type="string", description="password"),
])
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@schema(tobalncetransactionreport_schema)
def apiGetToBalanceTransactionHistory(request):
    username = request.data.get("username")
    userdetails = UserData.objects.get(username=username)
    try:
        bthist = balanceTransactionReport.objects.filter(destination=userdetails,category="BT").order_by('-date')
        if(bthist):
            data = BalanceTransferHistorySerializer(bthist,many=True)
            return Response({'success':True,'data':data.data},status=HTTP_200_OK)
        else:
            return Response({'success':False,'data':[]},status=HTTP_200_OK)
    except:
        return Response({'success':False,'message':'Something Unexpected Occured'},status=HTTP_200_OK)

tofundtransactionreport_schema = AutoSchema(manual_fields=[
    coreapi.Field("username", required=True, location="form", type="string", description="username"),
    coreapi.Field("password", required=True, location="form", type="string", description="password"),
])
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@schema(tofundtransactionreport_schema)
def apiGetToFundTransactionHistory(request):
    username = request.data.get("username")
    userdetails = UserData.objects.get(username=username)
    try:
        bthist = fundTransactionReport.objects.filter(destination=userdetails).order_by('-date')
        if(bthist):
            data = FundTransferHistorySerializer(bthist,many=True)
            return Response({'success':True,'data':data.data},status=HTTP_200_OK)
        else:
            return Response({'success':True,'data':[]},status=HTTP_200_OK)
    except:
        return Response({'success':False,'message':'Something Unexpected Occured'},status=HTTP_200_OK)

dcardstore_schema = AutoSchema(manual_fields=[
    coreapi.Field("username", required=True, location="form", type="string", description="username"),
    coreapi.Field("password", required=True, location="form", type="string", description="password"),
])
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@schema(dcardstore_schema)
def apiGetDcardStore(request):
    username = request.data.get("username")
    user = UserData.objects.get(username=username)
    btnlist=list()
    dproducts = datacardAssignments.objects.filter(assignedto=username).order_by('brand').values('brand__brand','margin')
    for i in dproducts:
        buttons=(i["brand__brand"]).split(" ")
        if buttons[0] not in btnlist:
            btnlist.append(buttons[0])
    content=list()
    if(len(btnlist)!=0):
        dcardproducts = datacardAssignments.objects.filter(assignedto=username,brand__brand__contains=btnlist[0]).order_by('brand').values('brand__brand','margin')
        for i in dcardproducts:
            dcp=datacardproducts.objects.filter(brand__brand=i["brand__brand"],status=True).order_by('brand').values('brand').annotate(count=Count('brand')).values('count','brand__id','brand__brand','brand__description','brand__denomination','brand__logo','count','brand__currency')
            if(len(dcp)>0):
                cost=getDatacardProductCost(username,dcp[0]["brand__brand"])
                data={'brand__id':dcp[0]['brand__id'],'brand__brand':dcp[0]['brand__brand'],'brand__logo':dcp[0]['brand__logo'],'brand__description':dcp[0]['brand__description'],'brand__currency':dcp[0]['brand__currency'],'count':dcp[0]['count'],'cost':cost}
                content.append(data)
        #data={'data':content,'fbuttons':btnlist}
        return Response({'success':True,'data':content,'fbuttons':btnlist},status=HTTP_200_OK)
    else:
        return Response({'success':True,'data':[]},status=HTTP_200_OK)

filtereddcardstore_schema = AutoSchema(manual_fields=[
    coreapi.Field("username", required=True, location="form", type="string", description="username"),
    coreapi.Field("password", required=True, location="form", type="string", description="password"),
    coreapi.Field("category", required=True, location="form", type="string", description="category"),
])
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@schema(filtereddcardstore_schema)
def apiGetFilteredDcardStore(request):
    username = request.data.get("username")
    brand = request.data.get("category")
    user = UserData.objects.get(username=username)
    btnlist=list()
    dproducts = datacardAssignments.objects.filter(assignedto=username).order_by('brand').values('brand__brand','margin')
    for i in dproducts:
        buttons=(i["brand__brand"]).split(" ")
        if buttons[0] not in btnlist:
            btnlist.append(buttons[0])
    content=list()
    if(len(btnlist)!=0):
        dcardproducts = datacardAssignments.objects.filter(assignedto=username,brand__brand__contains=brand).order_by('brand').values('brand__brand','margin')
        for i in dcardproducts:
            dcp=datacardproducts.objects.filter(brand__brand=i["brand__brand"],status=True).order_by('brand').values('brand').annotate(count=Count('brand')).values('count','brand__id','brand__brand','brand__description','brand__denomination','brand__logo','count','brand__currency')
            if(len(dcp)>0):
                cost=getDatacardProductCost(username,dcp[0]["brand__brand"])
                data={'brand__id':dcp[0]['brand__id'],'brand__brand':dcp[0]['brand__brand'],'brand__logo':dcp[0]['brand__logo'],'brand__description':dcp[0]['brand__description'],'brand__currency':dcp[0]['brand__currency'],'count':dcp[0]['count'],'cost':cost}
                content.append(data)
        #data={'data':content,'buttons':btnlist}
        return Response({'success':True,'data':content,'fbuttons':btnlist},status=HTTP_200_OK)
    else:
        return Response({'success':True,'data':[]},status=HTTP_200_OK)

dcardownbrand_schema = AutoSchema(manual_fields=[
    coreapi.Field("username", required=True, location="form", type="string", description="username"),
    coreapi.Field("password", required=True, location="form", type="string", description="password"),
])
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@schema(dcardownbrand_schema)
def apiGetDcardOwnBrandList(request):
    username = request.data.get("username")
    userdet = UserData.objects.get(username=username)
    if(userdet.postId!="Admin"):
        pdcts = datacardAssignments.objects.filter(assignedto=username).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand','brand__id','brand__logo','brand__currency','brand__description')
        return Response({'success':True,'data':pdcts},status=HTTP_200_OK)
    else:
        return Response({'success':False,'message':'Something Unexpected Occured'},status=HTTP_200_OK)

dcardpurchase_schema = AutoSchema(manual_fields=[
    coreapi.Field("username", required=True, location="form", type="string", description="username"),
    coreapi.Field("password", required=True, location="form", type="string", description="password"),
    coreapi.Field("brand", required=True, location="form", type="string", description="brand"),
    coreapi.Field("quantity", required=True, location="form", type="string", description="quantity"),
    coreapi.Field("amount", required=True, location="form", type="string", description="amount"),
])
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@schema(dcardpurchase_schema)
def apiGetDcardPurchase(request):
    try:
        username = request.data.get("username")
        brand = request.data.get("brand")
        quantity = request.data.get("quantity")
        amt = request.data.get("amount")
        branddet=dcardBrands.objects.get(brand=brand)
        userdet=UserData.objects.get(username=username)
        strlog = username+' buyed '+quantity+' '+brand
        #str = username+' Buyed '+str(quantity)+' '+brand+' by '+amount
        print(strlog)
        plog=PurchaseLog()
        plog.logdesc=strlog
        plog.save()
        ctime=datetime.now()
        time = timedelta(minutes = 5)
        now_minus_5 = ctime - time
        checkqty=datacardproducts.objects.filter(Q(brand__brand=brand) & Q(status=True) & (Q(sdate__isnull=True) | Q(sdate__lte=now_minus_5))).values('brand').annotate(productcount=Count('brand')).values('productcount')
        print(checkqty)
        needamt=0;
        result=list()
        licheckqty=list(checkqty)
        brand_id=0
        deno=0
        if(licheckqty[0]['productcount'] >= int(quantity)):
            usertype=''
            marginlist=list()
            margins=0
            count=0;
            flag=True
            prdct_id=''
            mllist=list()
            sponserlist=list()
            prdctdet = datacardproducts.objects.filter(Q(brand__brand=brand) & Q(status=True) & (Q(sdate__isnull=True) | Q(sdate__lte=now_minus_5)))[:int(quantity)]
            ctime = datetime.now()
            for i in prdctdet:
                i.productstatus=1
                i.suser = userdet
                i.sdate = ctime
                i.save()
            count=0
            admin=''
            while(True):
                userdet2=UserData.objects.filter(username=username).values('sponserId','postId','balance')
                margindet=datacardAssignments.objects.filter(assignedto=username,brand__brand=brand).values('margin')
                if(userdet2[0]['postId']=="Admin"):
                    admin=username
                    break;
                else:
                    cost=Decimal(amt)
                    prdctcost = (cost*Decimal(quantity))-(Decimal(margins)*Decimal(quantity))
                    margins=margins+Decimal(margindet[0]['margin'])
                    if(userdet2[0]['balance']>=prdctcost):
                        data={'margin':margindet[0]['margin'],'balance':userdet2[0]['balance'],'username':username,'prdctcost':prdctcost}
                        marginlist.append(data)
                        mllist.append(margindet[0]['margin'])
                        sponserlist.append(username)
                    else:
                        flag=False
                        break;
                username=userdet2[0]['sponserId']
            print(flag)
            if(flag):
                try:
                    prdctcddet=datacardproducts.objects.filter(brand__brand=brand,status=True,productstatus=1,suser=userdet,sdate=ctime)[:int(quantity)]
                    for h in prdctcddet:
                        h.status=False
                        h.save()
                        brand_id=h.brand.id
                        deno=h.brand.denomination
                        prdct_id=prdct_id+""+str(h.id)+","
                        res={"productid":h.id,"carduname":h.username,'brand':h.brand.brand,'brand_logo':h.brand.logo.url,'status':h.status,'suser':username,'sdate':convert_datetime_timezone(h.sdate),'description':branddet.description,'denomination':amt}
                        result.append(res)
                    ml=marginlist[::-1]
                    for k in ml:
                        uname = k['username']
                        margin = k['margin']
                        balance = k['balance']
                        pcost = k['prdctcost']
                        cb=Decimal(balance)-Decimal(pcost)
                        userd=UserData.objects.get(username=uname)
                        userd.balance=cb
                        userd.save()
                    mllen = len(mllist)
                    username = request.data.get("username")
                    closeuser = UserData.objects.get(username=username)
                    vcrep=vcloudtransactions()
                    vcrep.saleduser = userdet
                    vcrep.brand = brand
                    vcrep.type = "Dcard"
                    vcrep.brand_id = brand_id
                    vcrep.product_id = prdct_id
                    vcrep.quantity = quantity
                    vcrep.obalance = userdet.balance
                    vcrep.cbalance = closeuser.balance
                    vcrep.amount = amt
                    vcrep.rtype = "App"
                    vcrep.denominations = deno
                    ms = mllist[::-1]
                    mu = sponserlist[::-1]
                    ad=UserData.objects.get(username=admin)
                    if(mllen==1):
                        vcrep.margin1=ms[0]
                        vcrep.sponser1=ad
                        vcrep.sponser2=UserData.objects.get(username=sponserlist[0])
                    elif(mllen==2):
                        vcrep.margin1=ms[0]
                        vcrep.margin2=ms[1]
                        vcrep.sponser1=ad
                        vcrep.sponser2=UserData.objects.get(username=sponserlist[1])
                        vcrep.sponser3=UserData.objects.get(username=sponserlist[0])
                    else:
                        vcrep.margin1=ms[0]
                        vcrep.margin2=ms[1]
                        vcrep.margin3=ms[2]
                        vcrep.sponser1=ad
                        vcrep.sponser2=UserData.objects.get(username=sponserlist[2])
                        vcrep.sponser3=UserData.objects.get(username=sponserlist[1])
                        vcrep.sponser4=UserData.objects.get(username=sponserlist[0])
                    vcrep.save()
                    return Response({'success':True,'data':result},status=HTTP_200_OK)
                except:
                    return Response({'success':False,'message':'Sorry. You are requested product is buyed by Someone'},status=HTTP_200_OK)
            else:
                return Response({'success':False,'message':'Something Wrong May Happend, Try Again.! Else Contact Your Administrator'},status=HTTP_200_OK)
    except:
        return Response({'success':False,'message':'Something Unexpected Occured'},status=HTTP_200_OK)

dcardpurchaseProductReport_schema = AutoSchema(manual_fields=[
    coreapi.Field("username", required=True, location="form", type="string", description="username"),
    coreapi.Field("password", required=True, location="form", type="string", description="password"),
    coreapi.Field("id", required=True, location="form", type="string", description="transaction id"),
])
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@schema(dcardpurchaseProductReport_schema)
def apiGetPurchasedDcardProductReport(request):
    try:
        id = request.data.get("id")
        vcloudtxns=vcloudtransactions.objects.get(id=id)
        #print(vcloudtxns)
        productid=vcloudtxns.product_id
        result = productid.rstrip(',')
        pdid = result.split(',')
        pdlist=list()
        for i in pdid:
            pddet=datacardproducts.objects.get(id=i)
            data={"id":pddet.id,"brand":pddet.brand.brand,"username":pddet.username,"denomination":pddet.denomination,"logo":pddet.brand.logo.url,"date":pddet.sdate,"description":pddet.d}
            pdlist.append(data)
        return Response({'success':True,'data':pdlist},status=HTTP_200_OK)
    except:
        return Response({'success':False,'message':'Something Unexpected Happend'},status=HTTP_200_OK)

dcardpurchaseReport_schema = AutoSchema(manual_fields=[
    coreapi.Field("username", required=True, location="form", type="string", description="username"),
    coreapi.Field("password", required=True, location="form", type="string", description="password"),
])
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@schema(dcardpurchaseReport_schema)
def apiGetDcardPurchaseReport(request):
    try:
        username = request.data.get("username")
        content=list()
        noofrecords=0
        productsum =0
        quantitysum =0
        profitsum =0
        count=0
        userdet = UserData.objects.get(username=username)
        print(userdet)
        if(userdet.postId=='Reseller'):
            #print("Haiii")
            vcloudtxns=vcloudtransactions.objects.filter(sponser2__username=username,type="Dcard",rtype="App").order_by('-date')[:20]
            print(vcloudtxns)
            for i in vcloudtxns:
                print(i)
                cost=i.denominations+i.margin1
                productsum=productsum+(cost*i.quantity)
                quantitysum=quantitysum+i.quantity
                print(i)
                if(i.saleduser.username==username):
                    profit=0
                    data={"id":i.id,"saleduser":i.sponser2.name,"role":i.sponser2.postId,"date":convert_datetime_timezone(i.date),"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"denomination":i.denominations,"margin":0,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit}
                    content.append(data)
                    profitsum = profitsum+profit
                    count=count+1
                    print(data)
                else:
                    profit=i.margin2
                    data={"id":i.id,"saleduser":i.sponser3.name,"role":i.sponser3.postId,"date":convert_datetime_timezone(i.date),"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"denomination":i.denominations,"margin":i.margin2,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit}
                    content.append(data)
                    profitsum = profitsum+profit
                    count=count+1
                #print(content)
        elif(userdet.postId=='Sub_Reseller'):
            vcloudtxns=vcloudtransactions.objects.filter(sponser3__username=username,type="Dcard",rtype="App").order_by('-date')[:20]
            for i in vcloudtxns:
                cost=i.denominations+i.margin1+i.margin2
                productsum=productsum+(cost*i.quantity)
                quantitysum=quantitysum+i.quantity
                if(i.saleduser.username==username):
                    profit=0
                    data={"id":i.id,"saleduser":i.sponser3.name,"role":i.sponser3.postId,"date":convert_datetime_timezone(i.date),"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"denomination":i.denominations,"margin":0,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit}
                    content.append(data)
                    profitsum = profitsum+profit
                else:
                    profit=i.margin3
                    data={"id":i.id,"saleduser":i.sponser4.name,"role":i.sponser4.postId,"date":convert_datetime_timezone(i.date),"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"denomination":i.denominations,"margin":i.margin3,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit}
                    content.append(data)
                    profitsum = profitsum+profit
        else:
            vcloudtxns=vcloudtransactions.objects.filter(saleduser__username=username,type="Dcard",rtype="App").order_by('-date')[:20]
            for i in vcloudtxns:
                data={"id":i.id,"saleduser":i.saleduser.name,"role":i.saleduser.postId,"date":convert_datetime_timezone(i.date),"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"denomination":i.denominations,"margin":0,"quantity":i.quantity,"amount":(i.amount*i.quantity),"profit":0}
                content.append(data)
                productsum=productsum+(i.amount*i.quantity)
                quantitysum=quantitysum+i.quantity
                profitsum = 0
        print(content)
        if(len(content)==0):
            return Response({'success':True,'data':[]},status=HTTP_200_OK)
        else:
            data={"transaction":content,'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum}
            return Response({'success':True,'data':data},status=HTTP_200_OK)
    except:
        return Response({'success':False,'message':'Something Unexpected Happend'},status=HTTP_200_OK)

def vcloudlogtoproductdelete(request,id):
    try:
        print(id)
        det = vclouduplogs.objects.filter(id=id)
        det.delete()
        return redirect(addcsvProduct)
    except:
        return redirect(addcsvProduct)

def dcardlogtoproductdelete(request,id):
    try:
        print(id)
        det = dcarduplogs.objects.filter(id=id)
        det.delete()
        return redirect(adddcardcsvProduct)
    except:
        return redirect(adddcardcsvProduct)

def rcardlogtoproductdelete(request,id):
    try:
        print(id)
        det = rcarduplogs.objects.filter(id=id)
        det.delete()
        return redirect(addrcardcsvProduct)
    except:
        return redirect(addrcardcsvProduct)

# dcardpurchaseReport_schema = AutoSchema(manual_fields=[
#     coreapi.Field("username", required=True, location="form", type="string", description="username"),
#     coreapi.Field("password", required=True, location="form", type="string", description="password"),
#     coreapi.Field("fromdate", required=True, location="form", type="string", description="fromdate"),
#     coreapi.Field("todate", required=True, location="form", type="string", description="todate"),
#     coreapi.Field("user", required=True, location="form", type="string", description="user"),
#     coreapi.Field("brand", required=True, location="form", type="string", description="brand"),
# ])
# @csrf_exempt
# @api_view(["POST"])
# @permission_classes((AllowAny,))
# @schema(dcardpurchaseReport_schema)
# def apiGetDcardFilteredTransactionReport(request):
#     username=request.data.get("username")
#     fromdate=request.data.get("fromdate")
#     todate=request.data.get("todate")
#     fusername=request.data.get("user")
#     brand=request.data.get("brand")
#     content=list()
#     noofrecords=0
#     productsum =0
#     quantitysum =0
#     profitsum =0
#     try:
#         vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate,type="Dcard",brand=brand).order_by('-date')
#         for i in vcloudtxns:
#             saleduser=i.saleduser.username
#             saledusername=None
#             usertype=i.saleduser.postId
#             while(True):
#                 if(username==saleduser):
#                     margin=0
#                     profit=0
#                     name=UserData.objects.get(username=saleduser)
#                     if(name.username==fusername):
#                         data={"id":i.id,"saleduser":name.name,"role":usertype,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"denomination":i.denominations,"margin":margin,"quantity":i.quantity,"amount":(i.amount*i.quantity),"profit":profit}
#                         noofrecords=noofrecords+1
#                         productsum=productsum+(i.amount*i.quantity)
#                         quantitysum=quantitysum+i.quantity
#                         content.append(data)
#                         break
#                     else:
#                         break
#                 elif(username==saledusername):
#                     if(usertype1=="Admin"):
#                         margin=i.margin1
#                         profit=margin*i.quantity
#                         name=UserData.objects.get(username=saleduser)
#                         if(name.username==fusername):
#                             data={"id":i.id,"saleduser":name.name,"role":usertype,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"denomination":i.denominations,"margin":margin,"quantity":i.quantity,"amount":(i.amount*i.quantity),"profit":profit}
#                             content.append(data)
#                             noofrecords=noofrecords+1
#                             productsum=productsum+(i.amount*i.quantity)
#                             quantitysum=quantitysum+i.quantity
#                             profitsum=profitsum+profit
#                             break
#                         else:
#                             break
#                     else:
#                         margin=0
#                         if(usertype1=="Reseller"):
#                             margin=i.margin2
#                         elif(usertype1=="Sub_Reseller"):
#                             margin=i.margin3
#                         else:
#                             margin=i.margin4
#                         profit=margin*i.quantity
#                         name=UserData.objects.get(username=saleduser)
#                         if(name.username==fusername):
#                             data={"id":i.id,"saleduser":name.name,"role":usertype,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"denomination":i.denominations,"margin":margin,"quantity":i.quantity,"amount":(i.amount*i.quantity),"profit":profit}
#                             content.append(data)
#                             noofrecords=noofrecords+1
#                             productsum=productsum+(i.amount*i.quantity)
#                             quantitysum=quantitysum+i.quantity
#                             profitsum=profitsum+profit
#                             break
#                         else:
#                             break
#                 else:
#                     if(saledusername==None):
#                         saledusername=saleduser
#                     usdet=UserData.objects.get(username=saledusername)
#                     if(usdet.sponserId != None):
#                         saleduser=usdet.username
#                         usertype=usdet.postId
#                         saledusername=usdet.sponserId.username
#                         usertype1=usdet.sponserId.postId
#                     else:
#                         break
#         if(len(content)==0):
#             return Response({'success':True,'data':[]},status=HTTP_200_OK)
#         else:
#             data={"transaction":content,'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum}
#             return Response({'success':True,'data':data},status=HTTP_200_OK)
#     except:
#         return Response({'success':False,'mesage':'Something Unexpected Occured'},status=HTTP_200_OK)

rcardstore_schema = AutoSchema(manual_fields=[
    coreapi.Field("username", required=True, location="form", type="string", description="username"),
    coreapi.Field("password", required=True, location="form", type="string", description="password"),
])
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@schema(rcardstore_schema)
def apiGetRcardStore(request):
    username = request.data.get("username")
    user = UserData.objects.get(username=username)
    btnlist=list()
    content=list()
    dproducts = rcardAssignments.objects.filter(assignedto=username).order_by('brand').values('brand__brand','margin')
    for i in dproducts:
        buttons=(i["brand__brand"]).split(" ")
        if buttons[0] not in btnlist:
            btnlist.append(buttons[0])
    if(len(btnlist)!=0):
        dcardproducts = rcardAssignments.objects.filter(assignedto=username,brand__brand__contains=btnlist[0]).order_by('brand').values('brand__brand','margin')
        print(dcardproducts)
        for i in dcardproducts:
            dcp=rcardProducts.objects.filter(brand__brand=i["brand__brand"],status=True).order_by('brand').values('brand').annotate(count=Count('brand')).values('count','brand__id','brand__brand','brand__description','brand__denomination','brand__logo','brand__currency')
            if(len(dcp)>0):
                cost=getRcardProductCost(username,dcp[0]["brand__brand"])
                data={'brand__id':dcp[0]['brand__id'],'brand__brand':dcp[0]['brand__brand'],'brand__logo':dcp[0]['brand__logo'],'brand__description':dcp[0]['brand__description'],'brand__currency':dcp[0]['brand__currency'],'count':dcp[0]['count'],'cost':cost}
                content.append(data)
        #data={'data':content,'fbuttons':btnlist}
        return Response({'success':True,'data':content,'fbuttons':btnlist},status=HTTP_200_OK)
    else:
        return Response({'success':True,'data':[]},status=HTTP_200_OK)

filteredrcardstore_schema = AutoSchema(manual_fields=[
    coreapi.Field("username", required=True, location="form", type="string", description="username"),
    coreapi.Field("password", required=True, location="form", type="string", description="password"),
    coreapi.Field("category", required=True, location="form", type="string", description="category"),
])
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@schema(filteredrcardstore_schema)
def apiGetFilteredRcardStore(request):
    username = request.data.get("username")
    brand = request.data.get("category")
    user = UserData.objects.get(username=username)
    btnlist=list()
    content=list()
    dproducts = rcardAssignments.objects.filter(assignedto=username).order_by('brand').values('brand__brand','margin')
    for i in dproducts:
        buttons=(i["brand__brand"]).split(" ")
        if buttons[0] not in btnlist:
            btnlist.append(buttons[0])
    if(len(btnlist)!=0):
        dcardproducts = rcardAssignments.objects.filter(assignedto=username,brand__brand__contains=brand).order_by('brand').values('brand__brand','margin')
        for i in dcardproducts:
            dcp=rcardProducts.objects.filter(brand__brand=i["brand__brand"],status=True).order_by('brand').values('brand').annotate(count=Count('brand')).values('count','brand__id','brand__brand','brand__description','brand__denomination','brand__logo','count','brand__currency')
            if(len(dcp)>0):
                cost=getRcardProductCost(username,dcp[0]["brand__brand"])
                data={'brand__id':dcp[0]['brand__id'],'brand__brand':dcp[0]['brand__brand'],'brand__logo':dcp[0]['brand__logo'],'brand__description':dcp[0]['brand__description'],'brand__currency':dcp[0]['brand__currency'],'count':dcp[0]['count'],'cost':cost}
                content.append(data)
        #data={'data':content,'fbuttons':btnlist}
        return Response({'success':True,'data':content,'fbuttons':btnlist},status=HTTP_200_OK)
    else:
        return Response({'success':True,'data':[]},status=HTTP_200_OK)

rcardbrandlist_schema = AutoSchema(manual_fields=[
    coreapi.Field("username", required=True, location="form", type="string", description="username"),
    coreapi.Field("password", required=True, location="form", type="string", description="password"),
])
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@schema(rcardbrandlist_schema)
def apiGetRcardOwnBrandList(request):
    username = request.data.get("username")
    userdet = UserData.objects.get(username=username)
    if(userdet.postId!="Admin"):
        pdcts = rcardAssignments.objects.filter(assignedto=username).order_by('brand__brand').values('brand__brand').annotate(productcount=Count('brand')).values('brand','brand__brand','brand__id','brand__logo','brand__currency','brand__description')
        return Response({'success':True,'data':pdcts},status=HTTP_200_OK)
    else:
        return Response({'success':False,'message':'Something Unexpected Occur'},status=HTTP_200_OK)

rcardpurchasedproductreport_schema = AutoSchema(manual_fields=[
    coreapi.Field("username", required=True, location="form", type="string", description="username"),
    coreapi.Field("password", required=True, location="form", type="string", description="password"),
    coreapi.Field("id", required=True, location="form", type="string", description="transactionid"),
])
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@schema(rcardpurchasedproductreport_schema)
def apiGetPurchasedRcardProductReport(request):
    try:
        id = request.data.get("id")
        vcloudtxns=vcloudtransactions.objects.get(id=id)
        #print(vcloudtxns)
        productid=vcloudtxns.product_id
        result = productid.rstrip(',')
        pdid = result.split(',')
        pdlist=list()
        for i in pdid:
            pddet=rcardProducts.objects.get(id=i)
            data={"id":pddet.id,"brand":pddet.brand.brand,"username":pddet.username,"denomination":pddet.denomination,"logo":pddet.brand.logo.url}
            pdlist.append(data)
        return Response({'success':True,'data':pdlist},status=HTTP_200_OK)
    except:
        return Response({'success':False,'message':'Something Unexpected Occured'},status=HTTP_200_OK)

rcardpurchasedreport_schema = AutoSchema(manual_fields=[
    coreapi.Field("username", required=True, location="form", type="string", description="username"),
    coreapi.Field("password", required=True, location="form", type="string", description="password"),
])
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@schema(rcardpurchasedreport_schema)
def apiGetRcardPurchaseReport(request):
    try:
        username = request.data.get("username")
        content=list()
        noofrecords=0
        productsum =0
        quantitysum =0
        profitsum =0
        count=0
        userdet = UserData.objects.get(username=username)
        print(userdet)
        if(userdet.postId=='Reseller'):
            #print("Haiii")
            vcloudtxns=vcloudtransactions.objects.filter(sponser2__username=username,type="Rcard",rtype="App").order_by('-date')[:20]
            print(vcloudtxns)
            for i in vcloudtxns:
                print(i)
                cost=i.denominations+i.margin1
                productsum=productsum+(cost*i.quantity)
                quantitysum=quantitysum+i.quantity
                print(i)
                if(i.saleduser.username==username):
                    profit=0
                    data={"id":i.id,"saleduser":i.sponser2.name,"role":i.sponser2.postId,"date":convert_datetime_timezone(i.date),"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"denomination":i.denominations,"margin":0,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit}
                    content.append(data)
                    profitsum = profitsum+profit
                    count=count+1
                    print(data)
                else:
                    profit=i.margin2
                    data={"id":i.id,"saleduser":i.sponser3.name,"role":i.sponser3.postId,"date":convert_datetime_timezone(i.date),"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"denomination":i.denominations,"margin":i.margin2,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit}
                    content.append(data)
                    profitsum = profitsum+profit
                    count=count+1
                #print(content)
        elif(userdet.postId=='Sub_Reseller'):
            vcloudtxns=vcloudtransactions.objects.filter(sponser3__username=username,type="Rcard",rtype="App").order_by('-date')[:20]
            for i in vcloudtxns:
                cost=i.denominations+i.margin1+i.margin2
                productsum=productsum+(cost*i.quantity)
                quantitysum=quantitysum+i.quantity
                if(i.saleduser.username==username):
                    profit=0
                    data={"id":i.id,"saleduser":i.sponser3.name,"role":i.sponser3.postId,"date":convert_datetime_timezone(i.date),"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"denomination":i.denominations,"margin":0,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit}
                    content.append(data)
                    profitsum = profitsum+profit
                else:
                    profit=i.margin3
                    data={"id":i.id,"saleduser":i.sponser4.name,"role":i.sponser4.postId,"date":convert_datetime_timezone(i.date),"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"denomination":i.denominations,"margin":i.margin3,"quantity":i.quantity,"amount":(cost*i.quantity),"profit":profit}
                    content.append(data)
                    profitsum = profitsum+profit
        else:
            vcloudtxns=vcloudtransactions.objects.filter(saleduser__username=username,type="Rcard",rtype="App").order_by('-date')[:20]
            for i in vcloudtxns:
                data={"id":i.id,"saleduser":i.saleduser.name,"role":i.saleduser.postId,"date":convert_datetime_timezone(i.date),"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"denomination":i.denominations,"margin":0,"quantity":i.quantity,"amount":(i.amount*i.quantity),"profit":0}
                content.append(data)
                productsum=productsum+(i.amount*i.quantity)
                quantitysum=quantitysum+i.quantity
                profitsum = 0
        print(content)
        if(len(content)==0):
            return Response({'success':True,'data':[]},status=HTTP_200_OK)
        else:
            data={"transaction":content,'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum}
            return Response({'success':True,'data':data},status=HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({'success':False,'message':'Something Unexpected Occured'},status=HTTP_200_OK)

# rcardfilteredtransactionreport_schema = AutoSchema(manual_fields=[
#     coreapi.Field("username", required=True, location="form", type="string", description="username"),
#     coreapi.Field("password", required=True, location="form", type="string", description="password"),
#     coreapi.Field("fromdate", required=True, location="form", type="string", description="fromdate"),
#     coreapi.Field("todate", required=True, location="form", type="string", description="todate"),
#     coreapi.Field("user", required=True, location="form", type="string", description="user"),
#     coreapi.Field("brand", required=True, location="form", type="string", description="user"),
# ])
# @csrf_exempt
# @api_view(["POST"])
# @permission_classes((AllowAny,))
# @schema(rcardfilteredtransactionreport_schema)
# def apiGetRcardFilteredTransactionReport(request):
#     username=request.data.get("username")
#     fromdate=request.data.get("fromdate")
#     todate=request.data.get("todate")
#     fusername=request.data.get("user")
#     brand=request.data.get("brand")
#     content=list()
#     noofrecords=0
#     productsum =0
#     quantitysum =0
#     profitsum =0
#     try:
#         vcloudtxns=vcloudtransactions.objects.filter(date__gte=fromdate,date__lte=todate,type="Rcard",brand=brand).order_by('-date')
#         for i in vcloudtxns:
#             saleduser=i.saleduser.username
#             saledusername=None
#             usertype=i.saleduser.postId
#             while(True):
#                 if(username==saleduser):
#                     margin=0
#                     profit=0
#                     name=UserData.objects.get(username=saleduser)
#                     data={"id":i.id,"saleduser":name.name,"role":usertype,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"denomination":i.denominations,"margin":margin,"quantity":i.quantity,"amount":(i.amount*i.quantity),"profit":profit}
#                     noofrecords=noofrecords+1
#                     productsum=productsum+(i.amount*i.quantity)
#                     quantitysum=quantitysum+i.quantity
#                     content.append(data)
#                     break
#                 elif(username==saledusername):
#                     if(usertype1=="Admin"):
#                         margin=i.margin1
#                         profit=margin*i.quantity
#                         name=UserData.objects.get(username=saleduser)
#                         data={"id":i.id,"saleduser":name.name,"role":usertype,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"denomination":i.denominations,"margin":margin,"quantity":i.quantity,"amount":(i.amount*i.quantity),"profit":profit}
#                         content.append(data)
#                         noofrecords=noofrecords+1
#                         productsum=productsum+(i.amount*i.quantity)
#                         quantitysum=quantitysum+i.quantity
#                         profitsum=profitsum+profit
#                         break
#                     else:
#                         margin=0
#                         if(usertype1=="Reseller"):
#                             margin=i.margin2
#                         elif(usertype1=="Sub_Reseller"):
#                             margin=i.margin3
#                         else:
#                             margin=i.margin4
#                         profit=margin*i.quantity
#                         name=UserData.objects.get(username=saleduser)
#                         data={"id":i.id,"saleduser":name.name,"role":usertype,"date":i.date,"brand":i.brand,"type":i.type,"brand_id":i.brand_id,"product_id":i.product_id,"denomination":i.denominations,"margin":margin,"quantity":i.quantity,"amount":(i.amount*i.quantity),"profit":profit}
#                         content.append(data)
#                         noofrecords=noofrecords+1
#                         productsum=productsum+(i.amount*i.quantity)
#                         quantitysum=quantitysum+i.quantity
#                         profitsum=profitsum+profit
#                         break
#                 else:
#                     if(saledusername==None):
#                         saledusername=saleduser
#                     usdet=UserData.objects.get(username=saledusername)
#                     if(usdet.sponserId != None):
#                         saleduser=usdet.username
#                         usertype=usdet.postId
#                         saledusername=usdet.sponserId.username
#                         usertype1=usdet.sponserId.postId
#                     else:
#                         break
#         if(len(content)==0):
#             return Response({'success':True,'data':[]},status=HTTP_200_OK)
#         else:
#             data={"transaction":content,'productsum':productsum,'quantitysum':quantitysum,'profitsum':profitsum}
#             return Response({'success':True,'data':data},status=HTTP_200_OK)
#     except:
#         return Response({'success':False,'message':'Something Unexpected Occured'},status=HTTP_200_OK)

rcardpurchase_schema = AutoSchema(manual_fields=[
    coreapi.Field("username", required=True, location="form", type="string", description="username"),
    coreapi.Field("password", required=True, location="form", type="string", description="password"),
    coreapi.Field("brand", required=True, location="form", type="string", description="brand"),
    coreapi.Field("quantity", required=True, location="form", type="string", description="quantity"),
    coreapi.Field("amount", required=True, location="form", type="string", description="amount"),
])
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@schema(rcardpurchase_schema)
def apiGetRcardPurchase(request):
    try:
        username = request.data.get("username")
        brand = request.data.get("brand")
        quantity = request.data.get("quantity")
        amt = request.data.get("amount")
        branddet=rcardBrands.objects.get(brand=brand)
        userdet=UserData.objects.get(username=username)
        strlog = username+' buyed '+quantity+' '+brand
        #str = username+' Buyed '+str(quantity)+' '+brand+' by '+amount
        print(strlog)
        plog=PurchaseLog()
        plog.logdesc=strlog
        plog.save()
        ctime=datetime.now()
        time = timedelta(minutes = 5)
        now_minus_5 = ctime - time
        checkqty=rcardProducts.objects.filter(Q(brand__brand=brand) & Q(status=True) & (Q(sdate__isnull=True) | Q(sdate__lte=now_minus_5))).values('brand').annotate(productcount=Count('brand')).values('productcount')
        print(checkqty)
        needamt=0;
        result=list()
        licheckqty=list(checkqty)
        brand_id=0
        deno=0
        if(licheckqty[0]['productcount'] >= int(quantity)):
            usertype=''
            marginlist=list()
            margins=0
            count=0;
            flag=True
            prdct_id=''
            mllist=list()
            sponserlist=list()
            prdctdet = rcardProducts.objects.filter(Q(brand__brand=brand) & Q(status=True) & (Q(sdate__isnull=True) | Q(sdate__lte=now_minus_5)))[:int(quantity)]
            ctime = datetime.now()
            for i in prdctdet:
                i.productstatus=1
                i.suser = userdet
                i.sdate = ctime
                i.save()
            count=0
            admin=''
            while(True):
                userdet2=UserData.objects.filter(username=username).values('sponserId','postId','balance')
                margindet=rcardAssignments.objects.filter(assignedto=username,brand__brand=brand).values('margin')
                if(userdet2[0]['postId']=="Admin"):
                    admin=username
                    break;
                else:
                    cost=Decimal(amt)
                    prdctcost = (cost*Decimal(quantity))-(Decimal(margins)*Decimal(quantity))
                    margins=margins+Decimal(margindet[0]['margin'])
                    if(userdet2[0]['balance']>=prdctcost):
                        data={'margin':margindet[0]['margin'],'balance':userdet2[0]['balance'],'username':username,'prdctcost':prdctcost}
                        marginlist.append(data)
                        mllist.append(margindet[0]['margin'])
                        sponserlist.append(username)
                    else:
                        flag=False
                        break;
                username=userdet2[0]['sponserId']
            print(flag)
            if(flag):
                try:
                    prdctcddet=rcardProducts.objects.filter(brand__brand=brand,status=True,productstatus=1,suser=userdet,sdate=ctime)[:int(quantity)]
                    for h in prdctcddet:
                        h.status=False
                        h.save()
                        brand_id=h.brand.id
                        deno=h.brand.denomination
                        prdct_id=prdct_id+""+str(h.id)+","
                        res={"productid":h.id,"carduname":h.username,'brand':h.brand.brand,'brand_logo':h.brand.logo.url,'status':h.status,'suser':username,'sdate':convert_datetime_timezone(h.sdate),'description':branddet.description,'denomination':amt}
                        result.append(res)
                    ml=marginlist[::-1]
                    for k in ml:
                        uname = k['username']
                        margin = k['margin']
                        balance = k['balance']
                        pcost = k['prdctcost']
                        cb=Decimal(balance)-Decimal(pcost)
                        userd=UserData.objects.get(username=uname)
                        userd.balance=cb
                        userd.save()
                    mllen = len(mllist)
                    username = request.data.get("username")
                    closeuser = UserData.objects.get(username=username)
                    vcrep=vcloudtransactions()
                    vcrep.saleduser = userdet
                    vcrep.brand = brand
                    vcrep.type = "Rcard"
                    vcrep.obalance = userdet.balance
                    vcrep.cbalance = closeuser.balance
                    vcrep.brand_id = brand_id
                    vcrep.product_id = prdct_id
                    vcrep.quantity = quantity
                    vcrep.amount = amt
                    vcrep.rtype = "App"
                    vcrep.denominations = deno
                    ms = mllist[::-1]
                    mu = sponserlist[::-1]
                    print(ms)
                    print(admin)
                    ad=UserData.objects.get(username=admin)
                    if(mllen==1):
                        vcrep.margin1=ms[0]
                        vcrep.sponser1=ad
                        vcrep.sponser2=UserData.objects.get(username=sponserlist[0])
                    elif(mllen==2):
                        vcrep.margin1=ms[0]
                        vcrep.margin2=ms[1]
                        vcrep.sponser1=ad
                        vcrep.sponser2=UserData.objects.get(username=sponserlist[1])
                        vcrep.sponser3=UserData.objects.get(username=sponserlist[0])
                    else:
                        vcrep.margin1=ms[0]
                        vcrep.margin2=ms[1]
                        vcrep.margin3=ms[2]
                        vcrep.sponser1=ad
                        vcrep.sponser2=UserData.objects.get(username=sponserlist[2])
                        vcrep.sponser3=UserData.objects.get(username=sponserlist[1])
                        vcrep.sponser4=UserData.objects.get(username=sponserlist[0])
                    vcrep.save()
                    return Response({'success':True,'data':result},status=HTTP_200_OK)
                except:
                    return Response({'success':False,'message':'Something Wrong May Happend, Try Again.! Else Contact Your Administrator'},status=HTTP_200_OK)
            else:
                return Response({'success':False,'message':'Something Wrong May Happend, Try Again.! Else Contact Your Administrator'},status=HTTP_200_OK)
    except:
        return Response({'success':False,'message':'Something Unexpected Occured'},status=HTTP_200_OK)

def getAllMargin(request):
    if request.session.has_key("user"):
        if request.method == 'POST':
            username = request.session["user"]
            content = list()
            try:
                userdetails = UserData.objects.get(username=username)
                user = request.POST.get('username')
                type = request.POST.get('type', None)
                print(user)
                print(userdetails.username)
                print(type)
                muserdet = UserData.objects.get(username=user)
                if(type=="Vcloud"):
                    mdet = vcloudAssignments.objects.filter(assignedby=userdetails,assignedto=muserdet)
                    for i in mdet:
                        data={'brandid':i.brand.id,'margin':i.margin}
                        content.append(data)
                elif(type=="Dcard"):
                    mdet = datacardAssignments.objects.filter(assignedby=userdetails,assignedto=muserdet)
                    print(mdet)
                    for i in mdet:
                        data={'brandid':i.brand.id,'margin':i.margin}
                        content.append(data)
                else:
                    mdet = rcardAssignments.objects.filter(assignedby=userdetails,assignedto=muserdet)
                    for i in mdet:
                        data={'brandid':i.brand.id,'margin':i.margin}
                        content.append(data)
            except:
                pass;
            return JsonResponse(content,safe=False)
        else:
            return JsonResponse({"status":"Error"})
    else:
        return redirect(LoginPage)

def addAdvertisements(request):
    user = UserData.objects.get(username = request.session["user"])
    return render(request,"admin/vcloud/addads.html",{'form':AddPromotionForm,'user':user})

def submitadvertisements(request):
    if request.session.has_key("user"):
        if request.method == 'POST':
            print("Haiii")
            form = AddPromotionForm(request.POST, request.FILES)
            print("Haiii")
            print(form.errors)
            if form.is_valid():
                bd = form.save()
                messages.success(request, 'Added Successfully')
                return redirect(addAdvertisements)
            else:
                messages.warning(request, form.errors)
                return redirect(addAdvertisements)
        else:
            return redirect(addAdvertisements)
    else:
        return redirect(LoginPage)

getAdsImage_schema = AutoSchema(manual_fields=[
    coreapi.Field("username", required=True, location="form", type="string", description="username"),
    coreapi.Field("password", required=True, location="form", type="string", description="password"),
])
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@schema(getAdsImage_schema)
def apiGetImageAdvertisements(request):
    try:
        username = request.data.get("username")
        user = UserData.objects.get(username=username)
        ads = adverisements.objects.filter(usertype=user.postId, adtype="Image")
        if(len(ads)>0):
            adsdata=ImageAdsSerializer(ads,many=True)
            return Response({'success':True,'data':adsdata.data},status=status.HTTP_200_OK)
        else:
            return Response({'success':True,'data':[]},status=status.HTTP_200_OK)
    except:
        return Response({'success':False,'message':'Something Unexpected Occured'},status=status.HTTP_200_OK)

getAdsText_schema = AutoSchema(manual_fields=[
    coreapi.Field("username", required=True, location="form", type="string", description="username"),
    coreapi.Field("password", required=True, location="form", type="string", description="password"),
])
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
@schema(getAdsText_schema)
def apiGetTextAdvertisements(request):
    try:
        content=[]
        username = request.data.get("username")
        user = UserData.objects.get(username=username)
        ads = adverisements.objects.filter(usertype=user.postId)
        if(len(ads)>0):
            for i in ads:
                if(i.adtype=="Image"):
                    data={"type":i.adtype,"content":i.adimage.url}
                    content.append(data)
                else:
                    data={"type":i.adtype,"content":i.adtext}
                    content.append(data)
            return Response(content,status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_204_NO_CONTENT)
    except:
        return Response(status=HTTP_403_FORBIDDEN)


def viewAds(request):
    if request.session.has_key("user"):
        user = UserData.objects.get(username=request.session["user"])
        ads = adverisements.objects.all()
        return render(request,"admin/vcloud/promo.html",{'ads':ads,'user':user})
    else:
        return redirect(LoginPage)

def deleteAds(request,id):
    ads=adverisements.objects.get(id=id)
    ads.delete()
    return redirect(viewAds)

def deleteVcloudBrands(request,id):
    dt = vcloudBrands.objects.get(id=id)
    dt.delete()
    return redirect(manageVcloudBrands)

def deleteDcardBrands(request,id):
    dt = dcardBrands.objects.get(id=id)
    dt.delete()
    return redirect(manageDCardBrands)

def deleteRcardBrands(request,id):
    dt = rcardBrands.objects.get(id=id)
    dt.delete()
    return redirect(manageRCardBrands)


def dcardaddAdvertisements(request):
    user = UserData.objects.get(username = request.session["user"])
    return render(request,"admin/dcard/addads.html",{'form':AddPromotionForm,'user':user})

def dcardsubmitadvertisements(request):
    if request.session.has_key("user"):
        if request.method == 'POST':
            print("Haiii")
            form = AddPromotionForm(request.POST, request.FILES)
            print("Haiii")
            print(form.errors)
            if form.is_valid():
                bd = form.save()
                messages.success(request, 'Added Successfully')
                return redirect(dcardaddAdvertisements)
            else:
                messages.warning(request, form.errors)
                return redirect(dcardaddAdvertisements)
        else:
            return redirect(dcardaddAdvertisements)
    else:
        return redirect(LoginPage)


def dcardviewAds(request):
    if request.session.has_key("user"):
        user = UserData.objects.get(username=request.session["user"])
        ads = adverisements.objects.all()
        return render(request,"admin/dcard/promo.html",{'ads':ads,'user':user})
    else:
        return redirect(LoginPage)

def dcarddeleteAds(request,id):
    ads=adverisements.objects.get(id=id)
    ads.delete()
    return redirect(dcardviewAds)

def rcardaddAdvertisements(request):
    user = UserData.objects.get(username = request.session["user"])
    return render(request,"admin/rcard/addads.html",{'form':AddPromotionForm,'user':user})

def rcardsubmitadvertisements(request):
    if request.session.has_key("user"):
        if request.method == 'POST':
            print("Haiii")
            form = AddPromotionForm(request.POST, request.FILES)
            print("Haiii")
            print(form.errors)
            if form.is_valid():
                bd = form.save()
                messages.success(request, 'Added Successfully')
                return redirect(rcardaddAdvertisements)
            else:
                messages.warning(request, form.errors)
                return redirect(rcardaddAdvertisements)
        else:
            return redirect(rcardaddAdvertisements)
    else:
        return redirect(LoginPage)


def rcardviewAds(request):
    if request.session.has_key("user"):
        user = UserData.objects.get(username=request.session["user"])
        ads = adverisements.objects.all()
        return render(request,"admin/rcard/promo.html",{'ads':ads,'user':user})
    else:
        return redirect(LoginPage)

def rcarddeleteAds(request,id):
    ads=adverisements.objects.get(id=id)
    ads.delete()
    return redirect(rcardviewAds)

def deleteVcloudProduct(request,id):
    if request.session.has_key("user"):
        product=vcloudProducts.objects.get(id=id)
        product.delete()
        return redirect(vcloudmanageProduct)
    else:
        return redirect(LoginPage)

def deleteDcardProduct(request,id):
    if request.session.has_key("user"):
        product=datacardproducts.objects.get(id=id)
        product.delete()
        return redirect(dcardmanageProduct)
    else:
        return redirect(LoginPage)

def deleteRcardProduct(request,id):
    if request.session.has_key("user"):
        product=rcardProducts.objects.get(id=id)
        product.delete()
        return redirect(rcardmanageProduct)
    else:
        return redirect(LoginPage)

def uservcloudbtreport(request):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=request.session["user"])
        phist = balanceTransactionReport.objects.filter(destination=userdet).order_by('-date')
        return render(request,"user/vcloud/btReport.html",{'form':datefilterform,'user':userdet,'phist':phist})
    else:
        return redirect(LoginPage)

def filteruservcloudbtreport(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = datefilterform(request.POST or None)
            print(form.errors)
            if form.is_valid():
                currentuser=request.session["user"]
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                userdet=UserData.objects.get(username=currentuser)
                phist = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdet).order_by('-date')
                return render(request,"user/vcloud/btReport.html",{'form':datefilterform,'user':userdet,'phist':phist})
            else:
                return redirect(uservcloudbtreport)
        else:
            return redirect(uservcloudbtreport)
    else:
        return redirect(LoginPage)

def userdcardbtreport(request):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=request.session["user"])
        phist = balanceTransactionReport.objects.filter(destination=userdet).order_by('-date')
        return render(request,"user/dcard/btReport.html",{'form':datefilterform,'user':userdet,'phist':phist})
    else:
        return redirect(LoginPage)

def filteruserdcardbtreport(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = datefilterform(request.POST or None)
            print(form.errors)
            if form.is_valid():
                currentuser=request.session["user"]
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                userdet=UserData.objects.get(username=currentuser)
                phist = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdet).order_by('-date')
                return render(request,"user/vcloud/btReport.html",{'form':datefilterform,'user':userdet,'phist':phist})
            else:
                return redirect(userdcardbtreport)
        else:
            return redirect(userdcardbtreport)
    else:
        return redirect(LoginPage)

def userrcardbtreport(request):
    if request.session.has_key("user"):
        userdet=UserData.objects.get(username=request.session["user"])
        phist = balanceTransactionReport.objects.filter(destination=userdet).order_by('-date')
        return render(request,"user/dcard/btReport.html",{'form':datefilterform,'user':userdet,'phist':phist})
    else:
        return redirect(LoginPage)

def filteruserrcardbtreport(request):
    if request.session.has_key("user"):
        if request.method == "POST":
            form = datefilterform(request.POST or None)
            print(form.errors)
            if form.is_valid():
                currentuser=request.session["user"]
                fromdate=form.cleaned_data.get("fromdate")
                todate=form.cleaned_data.get("todate")
                userdet=UserData.objects.get(username=currentuser)
                phist = balanceTransactionReport.objects.filter(date__gte=fromdate,date__lte=todate,destination=userdet).order_by('-date')
                return render(request,"user/vcloud/btReport.html",{'form':datefilterform,'user':userdet,'phist':phist})
            else:
                return redirect(userrcardbtreport)
        else:
            return redirect(userrcardbtreport)
    else:
        return redirect(LoginPage)


def databasefix(request):
    vcloudtxns=vcloudtransactions.objects.filter(sponser1__isnull=True)
    print(vcloudtxns)
    count=0
    for i in vcloudtxns:
        username=i.saleduser.username
        data=list()
        while(True):
            user=UserData.objects.get(username=username)
            if(user.postId=="Admin"):
                #print(username)
                data.append(username)
                #print(count)
                break;
            else:
                #print(username)
                data.append(username)
                username=user.sponserId.username

        #print(data)
        print(len(data))
        if(len(data)==2):
            sponser1=UserData.objects.get(username=data[1])
            sponser2=UserData.objects.get(username=data[0])
            vd=vcloudtransactions.objects.get(id=i.id)
            vd.sponser1=sponser1
            vd.sponser2=sponser2
            vd.save()
            count=count+1
            print("success :"+str(count))
        elif(len(data)==3):
            print("Haiii")
            sponser1=UserData.objects.get(username=data[2])
            sponser2=UserData.objects.get(username=data[1])
            sponser3=UserData.objects.get(username=data[0])
            vd=vcloudtransactions.objects.get(id=i.id)
            vd.sponser1=sponser1
            vd.sponser2=sponser2
            vd.sponser3=sponser3
            vd.save()
            count=count+1
            print("success :"+str(count))
        elif(len(data)==4):
            sponser1=UserData.objects.get(username=data[3])
            sponser2=UserData.objects.get(username=data[2])
            sponser3=UserData.objects.get(username=data[1])
            sponser4=UserData.objects.get(username=data[0])
            vd=vcloudtransactions.objects.get(id=i.id)
            vd.sponser1=sponser1
            vd.sponser2=sponser2
            vd.sponser3=sponser3
            vd.sponser4=sponser4
            vd.save()
            count=count+1
            print("success :"+str(count))
    return redirect(vcloudhomepage)

def convert_datetime_timezone(dt):
    tz1 ="UTC"
    tz2 ="Asia/Riyadh"
    tz1 = pytz.timezone(tz1)
    tz2 = pytz.timezone(tz2)
    new_dt = str(dt)
    new_dt = new_dt[:19]
    dt = datetime.strptime(new_dt,"%Y-%m-%d %H:%M:%S")
    dt = tz1.localize(dt)
    dt = dt.astimezone(tz2)
    dt = dt.strftime("%b %d, %Y - %I:%M %p")
    return dt
