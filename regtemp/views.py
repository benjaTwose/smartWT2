# -*- coding: utf-8 -*-
import multiprocessing

from django.shortcuts import render

# Create your views here.

from datetime import datetime
from django.http import HttpResponse
from regtemp.models import Register
from regtemp.models import RegisterBkp
from regtemp.models import compute_statistics
from regtemp.models import Statistics


def register_temp(request,t_zone):
    """ This view is a call to register temp.
    it's used as API call for create a new reg in the database
    This is called from crontab or other external program
    """
    is_now = datetime.now()
    v_register = Register()
    v_register_temp = v_register.reg_temperature(t_zone)
    html = "<html><body>It is now %s. And temperature is %s</body></html>" % (is_now, v_register_temp)
    return HttpResponse(html)

def view_index(request):
    return render(request, template_name='index_template.html')


def view_statistics_data(request, n_day):
    data = Statistics.objects.filter(n_day=n_day).order_by('hour_minute')
    return render(request, template_name='chart_template_statistics.html', context={'data': data})


def view_register_data(request, n_day):
    nDay = n_day
    data = Register.objects.filter(date_reg_day=n_day).order_by('date_reg')
    return render(request, template_name='chart_template_register_v2.html', context={'data': data,'nDay':nDay})

def view_compute(request, n_day,t_zone):
    """ nday in isoweek format 1:Monday ..."""
    if request.method == 'GET':
        if n_day in range(1, 9):

                is_now = datetime.now()
                tst = multiprocessing.Process(target=compute_statistics, args=(n_day,t_zone,))
                tst.start()
                #degugg
                #compute_statistics(n_day)

                html = "<html><body>Launch compute day: %s, launch time: %s.<body></html>" % (n_day, is_now)
        else:
            html = "<html><body>bad request -> %s <body></html>" % (n_day)
    else:
        html = "<html><body>bad request<body></html>"


    return HttpResponse(html)


def view_register_hist_data(request):
    is_now = datetime.now()
    last_week = is_now - datetime.timedelta(days=6)
    data = RegisterBkp.objects.filter(date_reg > last_week).order_by('date_reg')
    return render(request, template_name='chart_template_register.html', context={'data': data,})
