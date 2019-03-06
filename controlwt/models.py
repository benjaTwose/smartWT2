from django.db import models
from datetime import datetime
from datetime import time
from smtconfigs.models import GeneralConfig
from regtemp.models import Statistics
from django.http import HttpResponse
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("This library don't work on this platform > " + str(RuntimeError))

GPIOPIN = 13


class RPiGpio_Status(models.Model):
    """ config and status for RPi.GPIO
    LED_PIN = 11 (GPIO 17)

    """


    out_1_pin = models.IntegerField()
    out_1_status = models.BooleanField()

    def turn_on(self):
        try:

            GPIO.setmode(GPIO.BOARD)
            GPIO.output(GPIOPIN, 1)
            self.out_1_status = 1
            self.save()
            return 1

        except RuntimeError:
            return -1

    def turn_off(self):
        try:
            GPIO.setmode(GPIO.BOARD)
            GPIO.output(GPIOPIN, 0)
            self.out_1_status = 0
            self.save()
            return 0

        except RuntimeError:
            return -1

    def __str__(self):
        return ("Out pin is: " + str(self.out_1_pin)
                + "and staus is: " + str(self.out_1_status)
                )




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


def control_on_off():
    """ power on / power of
    Conditions
    ControlPower: sets the time preference
    if there is a low/high rate setting, the control power works all time in low rate,
    but less time in high rate (for ex, 5 minutes on, 2 minutes off)

    Statistics: adds alternative conditions out of settings in ControlPower
    TO DO:  Call this function every ??  test needle
    """
    v_now = datetime.now().time()
    v_today = datetime.now().weekday()
    queryset = ControlPower.objects.filter(n_day__in=[8, v_today],
                                           hour_minute_on__lt=v_now,
                                           hour_minute_off__gt=v_now)
    queryset_st = Statistics.objects.filter(n_day=v_today, hour_minute=time(hour=v_now.hour, minute=v_now.minute))
    power_out = RPiGpio_Status()
    control_status = 0
    for field in queryset:
        try:
            if field.hour_minute_on <= datetime.now().time() <= field.hour_minute_off:
                control_status = 1
        except RuntimeError:
            print("Error in hour_minute_on/off")
            raise
    for field_st in queryset_st:
        try:
            if datetime.now().time().hour == field_st.hour_minute.hour \
                    and datetime.now().time().minute == field_st.hour_minute.minute \
                    and field_st.t_control == 1:
                control_status = 1
        except RuntimeError:
            print("Error in hour_minute_on/off")
            raise

    try:
        if control_status == 1:
            power_out.turn_on()
        else:
            power_out.turn_off()

    except RuntimeError:
        print("set power status fail:")
        raise






