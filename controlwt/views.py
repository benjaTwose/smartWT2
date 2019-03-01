from django.shortcuts import render
from regtemp.models import Statistics
from controlwt.models import ControlPower

from django.http import HttpResponse
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("This library don't work on this platform > " + str(RuntimeError))

# Create your models here.
LED_PIN = 7


def turn_on(request):
    try:
        GPIO.setmode(GPIO.BOARD)
        GPIO.output(LED_PIN, 1)
        return HttpResponse('')

    except RuntimeError:
        return HttpResponse('')


def turn_off(request):
    try:
        GPIO.setmode(GPIO.BOARD)
        GPIO.output(LED_PIN, 0)
        return HttpResponse('')

    except RuntimeError:
        return HttpResponse('')




