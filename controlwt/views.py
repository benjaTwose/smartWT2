from django.shortcuts import render
from regtemp.models import Statistics
from controlwt.models import control_on_off

from django.http import HttpResponse
try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print("This library don't work on this platform > " + str(RuntimeError))

# Create your models here.
GPIOPIN = 13


def turn_on(request):
    """ view to test out set to on """
    try:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(GPIOPIN, GPIO.OUT)
        GPIO.output(GPIOPIN, 1)
        return HttpResponse("<html><body>turn on </body></html>")

    except RuntimeError as e:
        html = "<html><body>error turn on ERROR: %s</body></html>" % (e)
        return HttpResponse(html)


def turn_off(request):
    """ view to test out set to off """
    try:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(GPIOPIN, GPIO.OUT)
        GPIO.output(GPIOPIN, 0)
        return HttpResponse("<html><body>turn on </body></html>")

    except RuntimeError as e:
        html = "<html><body>error turn off ERROR: %s</body></html>" % (e)
        return HttpResponse(html)


def api_on_off(request):
    """ view used as api call to set on/off power
    it can be called every 5 minutes for example """
    try:
        control_on_off()
        return HttpResponse("<html><body>call power on/off </body></html>")
    except RuntimeError as e:
        html = "<html><body>error launch auto control power: %s</body></html>" % (e)
        return HttpResponse(html)
