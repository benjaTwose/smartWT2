from django.contrib import admin
from controlwt.models import ControlPower
from controlwt.models import RPiGpio_Status


class ControlPowerAdmin(admin.ModelAdmin):
    pass

class RPiGpio_StatusAdmin(admin.ModelAdmin):
    pass


admin.site.register(ControlPower)
admin.site.register(RPiGpio_Status)


