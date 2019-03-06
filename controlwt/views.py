from django.shortcuts import render
from regtemp.models import Statistics
from controlwt.models import ControlPower

from django.http import HttpResponse
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("This library don't work on this platform > " + str(RuntimeError))

# Create your models here.
LED_PIN = 13


def turn_on(request):
    try:
        GPIO.setmode(GPIO.BOARD)
        GPIO.output(LED_PIN, 1)
        return HttpResponse("<html><body>turn on </body></html>")

    except RuntimeError as e:
        html = "<html><body>error turn on ERROR: %s</body></html>" % (e)
        return HttpResponse(html)


def turn_off(request):
    try:
        GPIO.setmode(GPIO.BOARD)
        GPIO.output(LED_PIN, 0)
        return HttpResponse("<html><body>turn on </body></html>")

    except RuntimeError as e:
        html = "<html><body>error turn off ERROR: %s</body></html>" % (e)
        return HttpResponse(html)




