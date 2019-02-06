from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print(RuntimeError)

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

