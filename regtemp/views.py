# -*- coding: utf-8 -*-
#from __future__ import unicode_literals

from django.shortcuts import render

# Create your views here.

from datetime import datetime
from django.http import HttpResponse
from regtemp.models import Register


def registertemp(request):
    is_now = datetime.now()
    v_register = Register()
    v_register_temp = v_register.reg_temperature()
    html = "<html><body>It is now %s. And temperature is %s</body></html>" % (is_now, v_register_temp)
    return HttpResponse(html)
