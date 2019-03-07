from django.db import models
from datetime import datetime
from datetime import time
from smtconfigs.models import GeneralConfig, ReducedRate
from django.utils import timezone
import pytz
import logging
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

    def __str__(self):
        return (str(self.id)
                + "-" + str(self.date_reg)
                + "-" + str(self.raw_temp)
                )

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
            self.date_reg = datetime.now(tz=pytz.timezone('Europe/Berlin'))
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

    def __str__(self):
        return (str(self.n_day)
                + "-" + str(self.hour_minute)
                + "-" + str(self.t_average)
                + "-" + str(self.t_count)
                + "-" + str(self.t_control)
                )

    def savedata(self, v_day, v_hour, v_minute, v_average, v_cnt):
        self.n_day = v_day
        self.hour_minute = time(hour=v_hour, minute=v_minute)
        if v_cnt > 0:
            self.t_average = v_average / v_cnt
        else:
            self.t_average = v_average
        self.t_count = v_cnt
        self.save()
        return 0

    def compute_control(self):
        ''' Compute the time to set power on and power off'''

        gc = GeneralConfig.objects.last()
        # TO DO: The reduced rate has filter parameters
        # disable and data ini data end to apply different reduced rates
        rr = ReducedRate.objects.filter(disable=0).last()
        if rr.hour_ini < self.hour_minute < rr.hour_end:
            day_rate = 'low'
        else:
            day_rate = 'high'

        # set time to power on conditioned by high / low rate
        time_power_on = gc.time_power_on_lr if day_rate =='low' else gc.time_power_on_hr
        time_power = time(hour=int(time_power_on/3600), minute=int((time_power_on%3600)/60), second=int((time_power_on%3600)%60))
        temp_trigger = gc.temp_trigger_lr if day_rate == 'low' else gc.temp_trigger_hr

        if time_power > time(hour=0, minute=0, second=0  ):
            if self.t_average > temp_trigger:
                self.t_control = 0
                self.save()
                diff_seconds = self.hour_minute.hour *3600 + self.hour_minute.minute*60 + self.hour_minute.second - time_power_on
                hm_range_ini = time(hour=int(diff_seconds/3600), minute=int((diff_seconds%3600)/60), second=int((diff_seconds%3600)%60))
                queryset = \
                    Statistics.objects.filter(n_day=self.n_day, hour_minute__range=[hm_range_ini, self.hour_minute])
                # set control on, on all registers in the range between
                # time inspected less the time configured as time_power_on
                if len(queryset) > 0 or True:
                    for field in queryset:
                        try:
                            field.t_control = 1
                            field.save()
                        except:
                            print("Unexpected error:", sys.exc_info()[0])
                            raise

            else:
                self.t_control = 0
        else:
            print("Configuration is not set. Can't calculate control trigger")


def compute_statistics(nday):
    """
    calculate the statistics from register.
    In first thought it will calculate the media value of every minute, separated in days of week
    over value configured, it controls on/of the warming of water.
    Then, only 30 days where calculated. The registers of raw data will be erased or transferred to another external db
    :parameters nday: day to make calc [1..8] - 1..7 is day week, 8 calculate all days
    :return:
    """
    logging.basicConfig(level=logging.DEBUG)
    if nday == 8:
        #calculate all week
        t_days = range(1, 8)
    elif nday in range(1, 8):
        # calculate only one day
        t_days = range(nday, (nday+1))
    else:
        t_days = 0
    t_hours = range(0, 24)
    t_minutes = range(0, 60)
    #print("ini ", datetime.now(), 'nday -> ', nday, 'range ', t_days)
    logging.debug("ini " + str(datetime.now()) + 'nday -> ' + str(nday) + 'range ' + str(t_days))
    for i_day in t_days:
        for i_hour in t_hours:
            for i_minute in t_minutes:
                logging.debug('calc average h:m ' + str(i_hour) + ' ' + str(i_minute))
                queryset = Register.objects.filter(date_reg__week_day=i_day,
                                                   date_reg__time__hour=i_hour, date_reg__time__minute=i_minute)
                cnt = 0
                calc_t_average = 0
                if len(queryset) > 0:
                    for field in queryset:
                        try:
                            calc_t_average = int(field.raw_temp) + int(calc_t_average)
                            cnt += 1
                            logging.debug('calc average ' + str((field.raw_temp)))
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

                    try:
                        # Update values if exists
                        sobj = Statistics.objects.get(n_day=i_day, hour_minute=time(hour=i_hour, minute=i_minute))
                        sobj.savedata(i_day, i_hour, i_minute, ((calc_t_average + sobj.t_average)/2), (cnt + sobj.t_count))
                        logging.debug('calc average ' +str(calc_t_average) + ' ' + str(sobj.t_average)+ ' '  + str(cnt)+ ' ' + str(sobj.t_count))
                    except Statistics.DoesNotExist:
                        # Create object values if not exists
                        sobj = Statistics()
                        Statistics.savedata(sobj, i_day, i_hour, i_minute, calc_t_average, cnt)
                        logging.debug('calc average new reg'  +str(calc_t_average) + ' ' + str(cnt) )
                        #print('calc average new reg', calc_t_average, cnt )

            if len(queryset) > 0:
                print(i_day, i_hour, i_minute, calc_t_average, cnt, len(queryset))

    queryset = Statistics.objects.all()
    if len(queryset) > 0:
        for field in queryset:
            try:
                field.compute_control()
            except:
                print("Unexpected error:", sys.exc_info()[0])
                raise

    print("end ", datetime.now())

