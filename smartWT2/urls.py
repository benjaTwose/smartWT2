"""smartWT2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url

from regtemp import views as regtemp_view
from controlwt import views as control_view
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    # This path is for create a new temperature register data
    path('regtemp/', regtemp_view.register_temp, name='regtemp'),
    url(r'turnOn', control_view.turn_on, name='turn_on'),
    url(r'turnOff', control_view.turn_off, name='turn_off'),
    path('compute/<int:n_day>', regtemp_view.view_compute, name='Compute'),
    url(r'apionoff', control_view.api_on_off, name='SetPower'),
    path('statistics/<int:n_day>', regtemp_view.view_statistics_data, name='Statistics'),
    path('register/<int:n_day>', regtemp_view.view_register_data, name='Register'),
    url(r'index',regtemp_view.view_index, name='index'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
