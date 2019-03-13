from django.contrib import admin
from controlwt.models import ControlPower
from controlwt.models import RPiGpio_Status


admin.site.register(ControlPower)
admin.site.register(RPiGpio_Status)