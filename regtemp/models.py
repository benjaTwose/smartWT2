from django.db import models
from datetime import datetime
from datetime import time
import locale
from smtconfigs.models import GeneralConfig
import sys


class RegisterBkp(models.Model):
    """ temperature register in raw data
    date_reg: data - time temperature read
    raw_temp: temperature in Cº x 1000 """
    date_reg = models.DateTimeField()
    raw_temp = models.IntegerField()


class Register(models.Model):
    """ temperature register in raw data
    date_reg: data - time temperature read
    raw_temp: temperature in Cº x 1000 """
    date_reg = models.DateTimeField()
    raw_temp = models.IntegerField()

    def get_temp_sens(self, datafilepath):
        """ get temp sens, get temperature data from senor
        :param datafilepath: path to file of sensor data

        """
        try:
            t_file = open(datafilepath)
            text = t_file.read()
            t_file.close()
            second_line = text.split("\n")[1]
            temperature_data = second_line.split(" ")[9]
            temperature = float(temperature_data[2:])
            # temperature = temperature / 1000
            # return RAW data
            return int(temperature)

        except IOError as e:
            print(e)
            return None

    def reg_temperature(self):
        """ insert data into register
            :param conn: connection to object
            :param regdata: values for  INSERT  statement
        """
        try:
            self.date_reg = datetime.now()
            self.raw_temp = self.get_temp_sens(str(GeneralConfig.objects.get(id=1).datafile))
            self.save()
            return self.raw_temp
        except IOError as e:
            print(e)


class Statistics(models.Model):
    """ temperature statistics to resolve control"""
    n_day = models.IntegerField()
    hour_minute = models.TimeField()
    t_average = models.IntegerField()
    t_count = models.IntegerField()
    t_control = models.BooleanField(default=False)

    def savedata(self, a, b, c, d, e):
        self.n_day = a
        self.hour_minute = time(hour=b, minute=c)
        if e > 0:
            self.t_average = d / e
        else:
            self.t_average = d
        self.t_count = e
        self.save()
        return 0

    def compute_control(self):
        ''' Compute the time to set power on and power off'''
        gc = GeneralConfig()
        time_power = gc.time_power_on_lr


        if len(gc) > 0:
            if self.t_average > GeneralConfig.temp_trigger_hr:
                self.t_control = 1
                queryset = Statistics.objects.filter(n_day=self.n_day,
                                                     hour_minute__range=[self.hour_minute,
                                                                         (self.hour_minute - gc.time_power)])
                # set control on, on all registers in the range
                # before the first detection occurred
                if len(queryset) > 0:
                    for field in queryset:
                        try:
                            field.t_control = 1
                        except:
                            print("Unexpected error:", sys.exc_info()[0])
                            raise

            else:
                self.t_control = 0
        else:
            print("Configuration is not set. Can't calculate control trigger")


def compute_statistics():
    """
    calculate the statistics from register.
    In first thought it will calculate the media value of every minute, separated in days of week
    over value configured, it controls on/of the warming of water.
    Then, only 30 days where calculated. The registers of raw data will be erased or transferred to another external db
    :return:
    """
    t_days = range(1, 8)
    t_hours = range(0, 24)
    t_minutes = range(0, 60)
    for i_day in t_days:
        for i_hour in t_hours:

            for i_minute in t_minutes:

                queryset = Register.objects.filter(date_reg__week_day=i_day,
                                                   date_reg__time__hour=i_hour, date_reg__time__minute=i_minute)
                cnt = 0
                calc_t_average = 0
                if len(queryset) > 0:
                    for field in queryset:
                        try:
                            calc_t_average = int(field.raw_temp) + int(calc_t_average)
                            cnt += 1

                            # bkp registers and delete raw data
                            rbkp = RegisterBkp()
                            rbkp.date_reg = field.date_reg
                            rbkp.raw_temp = field.raw_temp
                            rbkp.save()
                            field.delete()

                        except TypeError as e:
                            print(field.raw_temp, e.__cause__)
                        except:
                            print("Unexpected error:", sys.exc_info()[0])
                            raise
                    s = Statistics()
                    Statistics.savedata(s, i_day, i_hour, i_minute, calc_t_average, cnt)

            if len(queryset) > 0:
                print(i_day, i_hour, i_minute, calc_t_average, cnt, len(queryset))

    queryset = Statistics.objects.all()
    if len(queryset) > 0:
        for field in queryset:
            try:
                field.compute_control(field)
            except:
                print("Unexpected error:", sys.exc_info()[0])
                raise

