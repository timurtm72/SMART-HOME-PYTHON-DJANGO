from django.contrib import admin
from .models import *

admin.site.register(Device)
admin.site.register(SensorIndex)
admin.site.register(SensorBoolean)
admin.site.register(SensorInt)
admin.site.register(SensorFloat)
admin.site.register(SensorLogger)
admin.site.register(LogEntry)
