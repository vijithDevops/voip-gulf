from django import forms
from App.models import UserData
from App.models import *
from django.forms.widgets import SelectDateWidget
from datetime import timedelta

CURRENCY_CHOICE = (
    ('America (United States) Dollars - USD','America (United States) Dollars - USD'),
    ('Afghanistan Afghanis - AFN', 'Afghanistan Afghanis - AFN'),
    ('Albania Leke - ALL','Albania Leke - ALL'),
    ('Algeria Dinars - DZD','Algeria Dinars - DZD'),
    ('Argentina Pesos - ARS','Argentina Pesos - ARS'),
    ('Australia Dollars - AUD','Australia Dollars - AUD'),
    ('Austria Schillings - ATS', 'Austria Schillings - ATS'),
    ('Bahamas Dollars - BSD','Bahamas Dollars - BSD'),
    ('Bahrain Dinars - BHD','Bahrain Dinars - BHD'),
    ('Bangladesh Taka - BDT','Bangladesh Taka - BDT'),
    ('Barbados Dollars - BBD','Barbados Dollars - BBD'),
    ('Belgium Francs - BEF', 'Belgium Francs - BEF'),
    ('Bermuda Dollars - BMD','Bermuda Dollars - BMD'),
    ('Brazil Reais - BRL','Brazil Reais - BRL'),
    ('Bulgaria Leva - BGN','Bulgaria Leva - BGN'),
    ('Canada Dollars - CAD','Canada Dollars - CAD'),
    ('CFA BCEAO Francs - XOF', 'CFA BCEAO Francs - XOF'),
    ('CFA BEAC Francs - XAF','CFA BEAC Francs - XAF'),
    ('Chile Pesos - CLP','Chile Pesos - CLP'),
    ('China Yuan Renminbi - CNY','China Yuan Renminbi - CNY'),
    ('RMB (China Yuan Renminbi) - CNY','RMB (China Yuan Renminbi) - CNY'),
    ('Colombia Pesos - COP', 'Colombia Pesos - COP'),
    ('CFP Francs - XPF','CFP Francs - XPF'),
    ('Costa Rica Colones - CRC','Costa Rica Colones - CRC'),
    ('Croatia Kuna - HRK','Croatia Kuna - HRK'),
    ('Cyprus Pounds - CYP','Cyprus Pounds - CYP'),
    ('Czech Republic Koruny - CZK', 'Czech Republic Koruny - CZK'),
    ('Denmark Kroner - DKK','Denmark Kroner - DKK'),
    ('Deutsche (Germany) Marks - DEM','Deutsche (Germany) Marks - DEM'),
    ('Dominican Republic Pesos - DOP','Dominican Republic Pesos - DOP'),
    ('Dutch (Netherlands) Guilders - NLG','Dutch (Netherlands) Guilders - NLG'),
    ('Eastern Caribbean Dollars - XCD', 'Eastern Caribbean Dollars - XCD'),
    ('Egypt Pounds - EGP','Egypt Pounds - EGP'),
    ('Estonia Krooni - EEK','Estonia Krooni - EEK'),
    ('Euro - EUR','Euro - EUR'),
    ('Fiji Dollars - FJD','Fiji Dollars - FJD'),
    ('Finland Markkaa - FIM', 'Finland Markkaa - FIM'),
    ('France Francs - FRF*','France Francs - FRF*'),
    ('Germany Deutsche Marks - DEM','Germany Deutsche Marks - DEM'),
    ('Gold Ounces - XAU','Gold Ounces - XAU'),
    ('Greece Drachmae - GRD','Greece Drachmae - GRD'),
    ('Guatemalan Quetzal - GTQ', 'Guatemalan Quetzal - GTQ'),
    ('Holland (Netherlands) Guilders - NLG','Holland (Netherlands) Guilders - NLG'),
    ('Hong Kong Dollars - HKD','Hong Kong Dollars - HKD'),
    ('Hungary Forint - HUF','Hungary Forint - HUF'),
    ('Iceland Kronur - ISK','Iceland Kronur - ISK'),
    ('IMF Special Drawing Right - XDR', 'IMF Special Drawing Right - XDR'),
    ('India Rupees - INR','India Rupees - INR'),
    ('Indonesia Rupiahs - IDR','Indonesia Rupiahs - IDR'),
    ('Iran Rials - IRR','Iran Rials - IRR'),
    ('Iraq Dinars - IQD','Iraq Dinars - IQD'),
    ('Ireland Pounds - IEP*', 'Ireland Pounds - IEP*'),
    ('Israel New Shekels - ILS','Israel New Shekels - ILS'),
    ('Italy Lire - ITL*','Italy Lire - ITL*'),
    ('Jamaica Dollars - JMD','Jamaica Dollars - JMD'),
    ('Japan Yen - JPY','Japan Yen - JPY'),
    ('Jordan Dinars - JOD', 'Jordan Dinars - JOD'),
    ('Kenya Shillings - KES','Kenya Shillings - KES'),
    ('Korea (South) Won - KRW','Korea (South) Won - KRW'),
    ('Kuwait Dinars - KWD','Kuwait Dinars - KWD'),
    ('Lebanon Pounds - LBP','Lebanon Pounds - LBP'),
    ('Luxembourg Francs - LUF', 'Luxembourg Francs - LUF'),
    ('Malaysia Ringgits - MYR','Malaysia Ringgits - MYR'),
    ('Malta Liri - MTL','Malta Liri - MTL'),
    ('Mauritius Rupees - MUR','Mauritius Rupees - MUR'),
    ('Mexico Pesos - MXN','Mexico Pesos - MXN'),
    ('Morocco Dirhams - MAD', 'Morocco Dirhams - MAD'),
    ('Netherlands Guilders - NLG','Netherlands Guilders - NLG'),
    ('Nepalese Rupee - NPR','Nepalese Rupee - NPR'),
    ('New Zealand Dollars - NZD','New Zealand Dollars - NZD'),
    ('Norway Kroner - NOK','Norway Kroner - NOK'),
    ('Oman Rials - OMR', 'Oman Rials - OMR'),
    ('Pakistan Rupees - PKR','Pakistan Rupees - PKR'),
    ('Palladium Ounces - XPD','Palladium Ounces - XPD'),
    ('Peru Nuevos Soles - PEN','Peru Nuevos Soles - PEN'),
    ('Philippines Pesos - PHP','Philippines Pesos - PHP'),
    ('Platinum Ounces - XPT', 'Platinum Ounces - XPT'),
    ('Poland Zlotych - PLN','Poland Zlotych - PLN'),
    ('Portugal Escudos - PTE','Portugal Escudos - PTE'),
    ('Qatar Riyals - QAR','Qatar Riyals - QAR'),
    ('Romania New Lei - RON','Romania New Lei - RON'),
    ('Romania Lei - ROL', 'Romania Lei - ROL'),
    ('Russia Rubles - RUB','Russia Rubles - RUB'),
    ('Saudi Arabia Riyals - SAR','Saudi Arabia Riyals - SAR'),
    ('Silver Ounces - XAG','Silver Ounces - XAG'),
    ('Singapore Dollars - SGD','Singapore Dollars - SGD'),
    ('Slovakia Koruny - SKK', 'Slovakia Koruny - SKK'),
    ('Slovenia Tolars - SIT','Slovenia Tolars - SIT'),
    ('South Africa Rand - ZAR','South Africa Rand - ZAR'),
    ('South Korea Won - KRW','South Korea Won - KRW'),
    ('Spain Pesetas - ESP','Spain Pesetas - ESP'),
    ('Special Drawing Rights (IMF) - XDR', 'Special Drawing Rights (IMF) - XDR'),
    ('Sri Lanka Rupees - LKR','Sri Lanka Rupees - LKR'),
    ('Sudan Dinars - SDD','Sudan Dinars - SDD'),
    ('Sweden Kronor - SEK','Sweden Kronor - SEK'),
    ('Switzerland Francs - CHF','Switzerland Francs - CHF'),
    ('Taiwan New Dollars - TWD', 'Taiwan New Dollars - TWD'),
    ('Thailand Baht - THB','Thailand Baht - THB'),
    ('Trinidad and Tobago Dollars - TTD','Trinidad and Tobago Dollars - TTD'),
    ('Tunisia Dinars - TND','Tunisia Dinars - TND'),
    ('Turkey New Lira - TRY','Turkey New Lira - TRY'),
    ('United Arab Emirates Dirhams - AED', 'United Arab Emirates Dirhams - AED'),
    ('United Kingdom Pounds - GBP','United Kingdom Pounds - GBP'),
    ('United States Dollars - USD','United States Dollars - USD'),
    ('Venezuela Bolivares - VEB','Venezuela Bolivares - VEB'),
    ('Vietnam Dong - VND','Vietnam Dong - VND'),
    ('Zambia Kwacha - ZMK', 'Zambia Kwacha - ZMK'),
)

USER_CHOICE = (
    ('Reseller','Reseller'),
    ('User','User'),
)
USERTYPE_CHOICE = (
    ('Reseller','Reseller'),
    ('Sub_Reseller','Sub Reseller'),
    ('User','User'),
)
RESELLER_CHOICE = (
    ('Sub_Reseller','Reseller'),
    ('User','User'),
)

ADTYPE_CHOICE = (
    ('Image','Image'),
    ('Text','Text'),
)

VCLOUD_CHOICE = (
    ('card with cutting','Card With Cutting'),
    ('card without cutting','Card Without Cutting'),
)
BRANDTYPE_CHOICE = (
    ('Vcloud','Vcloud'),
    ('Dcard','Dcard'),
    ('Rcard','Rcard'),
)

class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=30, required=True)
    password = forms.CharField(max_length=30, required=True, widget=forms.PasswordInput)
    username.widget.attrs.update({'class': 'form-control','placeholder': 'Username'})
    password.widget.attrs.update({'class': 'form-control','placeholder': 'Password'})

class AddUserDataForm(forms.ModelForm):
    name = forms.CharField(max_length=30, required=True)
    address = forms.CharField(max_length=60, required=True, widget=forms.Textarea)
    mobileno = forms.CharField(max_length=30, required=True)
    username = forms.CharField(max_length=30, required=True)
    password = forms.CharField(max_length=30, required=True, widget=forms.PasswordInput)
    email = forms.EmailField(required=True)
    retailerLimit = forms.DecimalField(max_digits=20)
    margin = forms.DecimalField(max_digits=20, required=True)
    vcloud_status = forms.BooleanField()
    recharge_status = forms.BooleanField()
    name.widget.attrs.update({'class': 'form-control','placeholder': 'Name'})
    address.widget.attrs.update({'class': 'form-control','placeholder': 'Address'})
    mobileno.widget.attrs.update({'class': 'form-control','placeholder': 'Mobile No'})
    username.widget.attrs.update({'class': 'form-control','placeholder': 'Username','minlength':5})
    password.widget.attrs.update({'class': 'form-control','placeholder': 'Password'})
    email.widget.attrs.update({'class': 'form-control','placeholder': 'Email'})
    retailerLimit.widget.attrs.update({'class': 'form-control','placeholder': 'Retailer Limit'})
    margin.widget.attrs.update({'class': 'form-control','placeholder': 'Margin'})

    class Meta:
        model=UserData
        fields=('name','address','mobileno','username','password','email','retailerLimit','margin','vcloud_status','recharge_status')

class BalanceTransferForm(forms.Form):
    usertype = forms.CharField(max_length=20,required=True, widget=forms.Select())
    username = forms.CharField(max_length=120,required=True, widget=forms.Select())
    creditBalance = forms.DecimalField(max_digits=20, required=True)
    amount = forms.DecimalField(max_digits=20, required=True)
    creditBalance.widget.attrs.update({'class': 'form-control','placeholder': 'Credit Balance'})
    amount.widget.attrs.update({'class': 'form-control','placeholder': 'Amount'})

class AddVcloudBrands(forms.ModelForm):
    brand = forms.CharField(max_length=30, required=True)
    description = forms.CharField(max_length=60, required=True, widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}))
    denomination = forms.DecimalField(max_digits=20, required=True)
    category = forms.CharField(max_length=120,required=True, widget=forms.Select(choices=VCLOUD_CHOICE))
    logo = forms.ImageField(required=True)
    logo.widget.attrs.update({'onchange':'showImage(this);','class': 'form-control'})
    brand.widget.attrs.update({'class': 'form-control','placeholder': 'Brand Name'})
    description.widget.attrs.update({'class': 'form-control','placeholder': 'Description'})
    denomination.widget.attrs.update({'class': 'form-control','placeholder': 'Denomination'})
    category.widget.attrs.update({'class':'form-control'})

    class Meta:
        model = vcloudBrands
        fields = ('brand', 'description', 'denomination', 'category', 'logo')

class AddVcloudProducts(forms.Form):
    brand = forms.CharField(max_length=120,required=True, widget=forms.Select())
    username = forms.CharField(max_length=120,required=True)
    password = forms.CharField(max_length=120, required=True, widget=forms.PasswordInput)
    brand.widget.attrs.update({'class': 'form-control m-b'})
    username.widget.attrs.update({'class': 'form-control','placeholder': 'Username'})
    password.widget.attrs.update({'class': 'form-control','placeholder': 'Password'})

class editVcloudBrands(forms.Form):
    id = forms.IntegerField(required=True)
    brand = forms.CharField(max_length=30, required=True)
    desc = forms.CharField(max_length=60, required=True, widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}))
    rate = forms.DecimalField(max_digits=20, required=True)
    image = forms.ImageField(required=False)

class EditVcloudProducts(forms.Form):
    id = forms.IntegerField(required=True)
    username = forms.CharField(max_length=120, required=True)
    password = forms.CharField(max_length=120, required=True)

class EditCardProducts(forms.Form):
    id = forms.IntegerField(required=True)
    username = forms.CharField(max_length=120, required=True)

class UserEditForm(forms.Form):
    name = forms.CharField(max_length=30, required=True)
    address = forms.CharField(max_length=60, required=True, widget=forms.Textarea)
    mobileno = forms.CharField(max_length=30, required=True)
    iuser = forms.CharField(max_length=30)
    email = forms.EmailField(required=True)
    retailerLimit = forms.DecimalField(max_digits=20)
    margin = forms.DecimalField(max_digits=20, required=True)
    vcloud_status = forms.BooleanField()
    recharge_status = forms.BooleanField()

class AddDCardBrands(forms.ModelForm):
    brand = forms.CharField(max_length=30, required=True)
    description = forms.CharField(max_length=60, required=True, widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}))
    denomination = forms.DecimalField(max_digits=20, required=True)
    logo = forms.ImageField(required=True)
    logo.widget.attrs.update({'onchange':'showImage(this);','class': 'form-control'})
    brand.widget.attrs.update({'class': 'form-control','placeholder': 'Brand Name'})
    description.widget.attrs.update({'class': 'form-control','placeholder': 'Description'})
    denomination.widget.attrs.update({'class': 'form-control','placeholder': 'Denomination'})

    class Meta:
        model = dcardBrands
        fields = ('brand', 'description', 'denomination','logo')

class AddRCardBrands(forms.ModelForm):
    brand = forms.CharField(max_length=30, required=True)
    description = forms.CharField(max_length=60, required=True, widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}))
    denomination = forms.DecimalField(max_digits=20, required=True)
    logo = forms.ImageField(required=True)
    logo.widget.attrs.update({'onchange':'showImage(this);','class': 'form-control'})
    brand.widget.attrs.update({'class': 'form-control','placeholder': 'Brand Name'})
    description.widget.attrs.update({'class': 'form-control','placeholder': 'Description'})
    denomination.widget.attrs.update({'class': 'form-control','placeholder': 'Denomination'})

    class Meta:
        model = rcardBrands
        fields = ('brand', 'description', 'denomination','logo')

class editDcardBrands(forms.Form):
    id = forms.IntegerField(required=True)
    brand = forms.CharField(max_length=30, required=True)
    desc = forms.CharField(max_length=60, required=True, widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}))
    rate = forms.DecimalField(max_digits=20, required=True)
    image = forms.ImageField(required=False)

class editRcardBrands(forms.Form):
    id = forms.IntegerField(required=True)
    brand = forms.CharField(max_length=30, required=True)
    desc = forms.CharField(max_length=60, required=True, widget=forms.Textarea(attrs={'rows': 4, 'cols': 40}))
    rate = forms.DecimalField(max_digits=20, required=True)
    image = forms.ImageField(required=False)

class AddDcardProducts(forms.Form):
    brand = forms.CharField(max_length=120,required=True, widget=forms.Select())
    username = forms.CharField(max_length=120,required=True)
    brand.widget.attrs.update({'class': 'form-control m-b'})
    username.widget.attrs.update({'class': 'form-control','placeholder': 'Username'})

class AddRcardProducts(forms.Form):
    brand = forms.CharField(max_length=120,required=True, widget=forms.Select())
    username = forms.CharField(max_length=120,required=True)
    brand.widget.attrs.update({'class': 'form-control m-b'})
    username.widget.attrs.update({'class': 'form-control','placeholder': 'Username'})

class addvcloudproductascsv(forms.Form):
    brand = forms.CharField(max_length=120,required=True, widget=forms.Select())
    filename = forms.FileField(widget=forms.FileInput(attrs={'accept': ".csv"}))
    #filename = forms.FileField(required=True)
    brand.widget.attrs.update({'class': 'form-control m-b'})
    filename.widget.attrs.update({'class': 'form-control'})

class adddcardproductascsv(forms.Form):
    brand = forms.CharField(max_length=120,required=True, widget=forms.Select())
    filename = forms.FileField(widget=forms.FileInput(attrs={'accept': ".csv"}))
    #filename = forms.FileField(required=True)
    brand.widget.attrs.update({'class': 'form-control m-b'})
    filename.widget.attrs.update({'class': 'form-control'})

class addrcardproductascsv(forms.Form):
    brand = forms.CharField(max_length=120,required=True, widget=forms.Select())
    filename = forms.FileField(widget=forms.FileInput(attrs={'accept': ".csv"}))
    #filename = forms.FileField(required=True)
    brand.widget.attrs.update({'class': 'form-control m-b'})
    filename.widget.attrs.update({'class': 'form-control'})

class vcloudDashboardfilter(forms.Form):
    fromdate = forms.DateField(initial=datetime.now()-timedelta(days=1))
    todate = forms.DateField(initial=datetime.now())
    usertype = forms.CharField(max_length=120,required=True, widget=forms.Select())
    username = forms.CharField(max_length=120,required=True, widget=forms.Select())
    fromdate.widget.attrs.update({'class': 'form-control datetime-input'})
    todate.widget.attrs.update({'class': 'form-control datetime-input'})
    usertype.widget.attrs.update({'class': 'form-control m-b'})
    username.widget.attrs.update({'class': 'form-control m-b'})

class uservclouddashboardfilter(forms.Form):
    fromdate = forms.DateField(initial=datetime.now()-timedelta(days=1))
    todate = forms.DateField(initial=datetime.now())
    fromdate.widget.attrs.update({'class': 'form-control datetime-input'})
    todate.widget.attrs.update({'class': 'form-control datetime-input'})
    #fromdate.widget.attrs.update({'class': 'form-control input-daterange-datepicker'})

class dcardDashboardfilter(forms.Form):
    fromdate = forms.DateField(initial=datetime.now()-timedelta(days=1))
    todate = forms.DateField(initial=datetime.now())
    usertype = forms.CharField(max_length=120,required=True, widget=forms.Select())
    username = forms.CharField(max_length=120,required=True, widget=forms.Select())
    fromdate.widget.attrs.update({'class': 'form-control datetime-input'})
    todate.widget.attrs.update({'class': 'form-control datetime-input'})
    usertype.widget.attrs.update({'class': 'form-control m-b'})
    username.widget.attrs.update({'class': 'form-control m-b'})

class userdcardDashboardfilter(forms.Form):
    fromdate = forms.DateField(initial=datetime.now()-timedelta(days=1))
    todate = forms.DateField(initial=datetime.now())
    fromdate.widget.attrs.update({'class': 'form-control datetime-input'})
    todate.widget.attrs.update({'class': 'form-control datetime-input'})

class rcardDashboardfilter(forms.Form):
    fromdate = forms.DateField(initial=datetime.now()-timedelta(days=1))
    todate = forms.DateField(initial=datetime.now())
    usertype = forms.CharField(max_length=120,required=True, widget=forms.Select())
    username = forms.CharField(max_length=120,required=True, widget=forms.Select())
    fromdate.widget.attrs.update({'class': 'form-control datetime-input'})
    todate.widget.attrs.update({'class': 'form-control datetime-input'})
    usertype.widget.attrs.update({'class': 'form-control m-b'})
    username.widget.attrs.update({'class': 'form-control m-b'})

class userrcardDashboardfilter(forms.Form):
    fromdate = forms.DateField(initial=datetime.now())
    todate = forms.DateField(initial=datetime.now())
    fromdate.widget.attrs.update({'class': 'form-control datetime-input'})
    todate.widget.attrs.update({'class': 'form-control datetime-input'})

class vcloudreportfilterform(forms.Form):
    fromdate = forms.DateField(initial=datetime.now()-timedelta(days=1))
    todate = forms.DateField(initial=datetime.now())
    usertype = forms.CharField(max_length=120,required=False, widget=forms.Select())
    username = forms.CharField(max_length=120,required=False, widget=forms.Select())
    type = forms.CharField(max_length=120,required=False, widget=forms.Select(choices=BRANDTYPE_CHOICE))
    brand = forms.CharField(max_length=120,required=False, widget=forms.Select())
    fromdate.widget.attrs.update({'class': 'form-control datetime-input'})
    todate.widget.attrs.update({'class': 'form-control datetime-input'})
    usertype.widget.attrs.update({'class': 'form-control m-b'})
    username.widget.attrs.update({'class': 'form-control m-b'})
    type.widget.attrs.update({'class': 'form-control m-b'})
    brand.widget.attrs.update({'class': 'form-control m-b'})

class uservcloudreportfilterform(forms.Form):
    fromdate = forms.DateField(initial=datetime.now()-timedelta(days=1))
    todate = forms.DateField(initial=datetime.now())
    type = forms.CharField(max_length=120,required=True, widget=forms.Select(choices=BRANDTYPE_CHOICE))
    brand = forms.CharField(max_length=120,required=True, widget=forms.Select())
    fromdate.widget.attrs.update({'class': 'form-control datetime-input'})
    todate.widget.attrs.update({'class': 'form-control datetime-input'})
    type.widget.attrs.update({'class': 'form-control m-b'})
    brand.widget.attrs.update({'class': 'form-control m-b'})

class balancetransferfilterform(forms.Form):
    fromdate = forms.DateField(initial=datetime.now()-timedelta(days=1))
    todate = forms.DateField(initial=datetime.now())
    usertype = forms.CharField(max_length=120,required=False, widget=forms.Select())
    username = forms.CharField(max_length=120,required=True, widget=forms.Select())
    fromdate.widget.attrs.update({'class': 'form-control datetime-input'})
    todate.widget.attrs.update({'class': 'form-control datetime-input'})
    usertype.widget.attrs.update({'class': 'form-control m-b'})
    username.widget.attrs.update({'class': 'form-control m-b'})

class paymentfilterform(forms.Form):
    fromdate = forms.DateField(initial=datetime.now()-timedelta(days=1))
    todate = forms.DateField(initial=datetime.now())
    usertype = forms.CharField(max_length=120,required=True, widget=forms.Select())
    username = forms.CharField(max_length=120,required=True, widget=forms.Select())
    fromdate.widget.attrs.update({'class': 'form-control datetime-input'})
    todate.widget.attrs.update({'class': 'form-control datetime-input'})
    usertype.widget.attrs.update({'class': 'form-control m-b'})
    username.widget.attrs.update({'class': 'form-control m-b'})

class changepassword(forms.Form):
    cpassword = forms.CharField(max_length=120, required=True, widget=forms.PasswordInput)
    npassword = forms.CharField(max_length=120, required=True, widget=forms.PasswordInput)
    cnpassword = forms.CharField(max_length=120, required=True, widget=forms.PasswordInput)
    cpassword.widget.attrs.update({'class': 'form-control','placeholder': 'Current Password'})
    npassword.widget.attrs.update({'class': 'form-control','placeholder': 'New Password'})
    cnpassword.widget.attrs.update({'class': 'form-control','placeholder': 'Confirm New Password'})

class datefilterform(forms.Form):
    fromdate = forms.DateField(initial=datetime.now()-timedelta(days=1))
    todate = forms.DateField(initial=datetime.now())
    fromdate.widget.attrs.update({'class': 'form-control datetime-input'})
    todate.widget.attrs.update({'class': 'form-control datetime-input'})

class AddPromotionForm(forms.ModelForm):
    usertype = forms.CharField(max_length=120,required=True, widget=forms.Select(choices=USERTYPE_CHOICE))
    ctype = forms.CharField(max_length=120,required=True, widget=forms.Select(choices=BRANDTYPE_CHOICE))
    adtype = forms.CharField(max_length=120,required=True, widget=forms.Select(choices=ADTYPE_CHOICE))
    adimage = forms.ImageField(required=False)
    adtext = forms.CharField(max_length=500, required=False)
    usertype.widget.attrs.update({'class': 'form-control m-b'})
    adtype.widget.attrs.update({'class': 'form-control m-b'})
    adimage.widget.attrs.update({'class': 'form-control'})
    adtext.widget.attrs.update({'class': 'form-control','placeholder': 'Ad Text'})
    ctype.widget.attrs.update({'class': 'form-control m-b'})

    class Meta:
        model = adverisements
        fields = ('usertype', 'ctype', 'adtype','adimage','adtext')
