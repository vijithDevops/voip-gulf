from django.contrib.auth.models import User
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from App.models import UserData
import hashlib

class MyCustomAuthentication(BaseAuthentication):
    def authenticate(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        print(username)
        print(password)
        if not username: # no username passed in request headers
            return None # authentication did not succeed
        hashkey = username+password
        hash = hashlib.sha256(hashkey.encode()).hexdigest()
        try:
            user = UserData.objects.get(username = username, password = hash)
        except:
            raise exceptions.AuthenticationFailed('Invalid username/password.')
