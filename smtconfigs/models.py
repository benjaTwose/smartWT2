# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


# generic models. program configs


class ReducedRate(models.Model):
    """ data table to specify the reduced rate if aplicable
    it is used to reduce the time that term is warming up the water
    during high range rate """
    data_ini = models.DateField()
    data_end = models.DateField()
    hour_ini = models.TimeField()
    hour_end = models.TimeField()
    disable = models.BooleanField(default=False)

    def __str__(self):
        return (str(self.data_ini)
                + "-" + str(self.data_end)
                + "-" + str(self.hour_ini)
                + "-" + str(self.hour_end)
                + "- disabled? " + str(self.disable)
                )


class GeneralConfig(models.Model):
    # ,default='/sys/bus/w1/devices/28-000006961afe/w1_slave'
    datafile = models.CharField(max_length=200)

    def __unicode__(self):
        return '%s' % self.datafile


