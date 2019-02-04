

from django.contrib import admin
from smtconfigs.models import GeneralConfig
from smtconfigs.models import ReducedRate


admin.site.register(GeneralConfig)
admin.site.register(ReducedRate)


#
# from django.contrib import admin
# from django.db.models import Model
# import inspect
# from . import models
# for name, obj in inspect.getmembers(models):
#     if inspect.isclass(obj) and issubclass(obj, Model):
#         admin.site.register(obj)
#         print('admin.py this is  - ' + str(name) + str(obj))
# #    else:
# #        print('admin.py this is not a class and subclass object' + str(obj))
