from django.db import models
from datetime import datetime
from smtconfigs.models import GeneralConfig
from regtemp.models import Statistics


class ControlPower(models.Model):
    """ power control
    parameters:
    n_day: 1 to 7, day of week.  8 applies to every day
    hour_minute_on: set on power switch
    hour_minute_off: set of power switch
    """
    n_day = models.IntegerField()
    hour_minute_on = models.TimeField()
    hour_minute_off = models.TimeField()

    def __str__(self):
        return (str(self.n_day)
                + "-" + str(self.hour_minute_on)
                + "-" + str(self.hour_minute_off)
                )

