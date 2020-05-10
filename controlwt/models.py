from django.db import models
from datetime import datetime
from datetime import time
from datetime import timedelta
from regtemp.models import Statistics
import logging

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
    created_at = models.DateTimeField(auto_now_add=True)
    GPIO.setwarnings(False)

    def turn_on(self):
        try:

            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(GPIOPIN, GPIO.OUT)
            GPIO.output(GPIOPIN, 1)
            self.out_1_pin = GPIOPIN
            self.out_1_status = 1
            logging.debug("turn on pin/status " + str(GPIOPIN) + '/' + str(self.out_1_status))
            self.save()
            return 1

        except RuntimeError as e:
            logging.error("Error in turn on: " + str(e))
            return -1

    def turn_off(self):
        try:
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(GPIOPIN, GPIO.OUT)
            GPIO.output(GPIOPIN, 0)
            self.out_1_pin = GPIOPIN
            self.out_1_status = 0
            self.save()
            return 0

        except RuntimeError as e:
            logging.error("Error in turn on: " + str(e))
            return -1

    def __str__(self):
        return ("Out pin is: " + str(self.out_1_pin)
                + " and staus is: " + str(self.out_1_status)
                + " created: " + str(self.created_at)
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
    # debug -----------------------------------------------
    logging.basicConfig(level=logging.DEBUG)
    logging.debug("init control on off")
    # -----------------------------------------------------

    """
    Set on/off from default week settings
    """
    v_nowd = datetime.utcnow()
    v_now = v_nowd.time()
    v_now_add = (v_nowd + timedelta(minutes=5)).time()
    v_today = datetime.utcnow().isoweekday()
    queryset = ControlPower.objects.filter(n_day__in=[8, v_today],
                                           hour_minute_on__lt=v_now,
                                           hour_minute_off__gt=v_now_add)
    power_out = RPiGpio_Status()
    control_status = 0
    for field in queryset:
        try:
            # TO DO -> time is in utc and hour minute in local time - calculate deltas
            logging.debug("control_on_off " + str(field.hour_minute_on) + ' <= ' + str(datetime.utcnow().time()) +
                          ' <= ' + str(field.hour_minute_off))
            if field.hour_minute_on <= datetime.utcnow().time() <= field.hour_minute_off:
                control_status = 1
        except RuntimeError:
            logging.error("Error in hour_minute_on/off")
            raise


    """
    Set on/off from statistics 
    """
    #queryset_st = Statistics.objects.filter(n_day=v_today, hour_minute=time(hour=v_now.hour, minute=v_now.minute))
    queryset_st = Statistics.objects.filter(n_day=v_today,
                                            hour_minute__gte=time(hour=v_now.hour, minute=(v_now.minute)),
                                            hour_minute__lte=time(hour=v_now_add.hour, minute=(v_now_add.minute)))
    """ It's needle to have one register per day to use statistics"""
    if len(queryset_st) > 0:
        for field_st in queryset_st:
            try:
                if datetime.utcnow().time().hour == field_st.hour_minute.hour \
                        and  datetime.utcnow().time().minute == field_st.hour_minute.minute \
                        and field_st.t_control == 1:

                    if field_st.t_count>1:
                        """ It's needle to have more than one counter per minute to use statistics"""
                        logging.debug("control_on_off  -> statistics set -> control_status = 1")
                        control_status = 1
            except RuntimeError as e:
                logging.error("Error in hour_minute_on/off: %s", e)
                raise
    else:
        control_status = 1
    try:
        if control_status == 1:
            power_out.turn_on()
        else:
            power_out.turn_off()

    except RuntimeError as e:
        logging.error("set power status fail, Error: %s", e)
        raise






