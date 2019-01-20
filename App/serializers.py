from rest_framework import serializers
from . models import *

class UserDataSerializer(serializers.ModelSerializer):
    post = serializers.CharField(source='postId')
    credit = serializers.DecimalField(source='targetAmt',max_digits=20,decimal_places=2)
    class Meta:
        model=UserData
        fields=('username','name','post','balance','credit')

class ResellerOrUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model=UserData
        fields=('username','name','postId')

class SingleUserDetailsSerializer(serializers.ModelSerializer):
    post = serializers.CharField(source='postId')
    sponser = serializers.CharField(source='sponserId')
    credit = serializers.DecimalField(source='targetAmt',max_digits=20,decimal_places=2)
    limit = serializers.DecimalField(source='retailerLimit',max_digits=20,decimal_places=2)
    class Meta:
        model=UserData
        fields=('username','name','address','email','mobileno','post','sponser','status','balance','limit','credit')

class BalanceTransferHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = balanceTransactionReport
        fields = ('category','source','destination','amount','remarks','date')

class FundTransferHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = fundTransactionReport
        fields = ('source','destination','amount','remarks','date')

class VcloudProductDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = vcloudProducts
        fields= '__All__'

class ImageAdsSerializer(serializers.ModelSerializer):
    class Meta:
        model = adverisements
        fields = ('usertype','ctype','adimage') 

class TextAdsSerializer(serializers.ModelSerializer):
    class Meta:
        model = adverisements
        fields = ('adtype','usertype','ctype','adtext','adimage') 
