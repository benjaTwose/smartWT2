from django.db import models
from datetime import datetime
from smtconfigs.models import GeneralConfig


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
            print (e)
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

    def calc_statistics(self):
        """
        calculate the statistics from register.
        In first thought it will calculate the media value of every minute, separated in days of week
        over value configured, it controls on/of the warming of water.
        Then, only 30 days where calculated. The registers of raw data will be erased or transferred to another external db
        :return:
        """
        calc_data = Register()

