from django.db import models
from django.contrib.auth.models import User
import datetime
from django.core.validators import MinValueValidator, MaxValueValidator

class DevicesPerUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    number_of_devices =models.IntegerField(blank=False, null=False, default=0)

class Device(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device_id = models.IntegerField(blank=False, null=False,default=0)
    label = models.CharField(blank=False, max_length=50)
    description = models.CharField(blank=True, max_length=200)
    last_connection = models.DateField( auto_now=True)
    number_of_sensors=models.IntegerField(blank=False, default=0, null=False)
    def __str__(self):
        return str(self.pk)


tipo_sensor=((1,"SensorBoolean"),(2,"SensorInt"),(3,"SensorFloat"))

class SensorIndex(models.Model):
    ''' relates a device with every child sensor of differents kinds'''
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    sensor_id = models.IntegerField(blank=False, null=False, default=-1)
    tipo =models.IntegerField(blank=False, null=False,choices=tipo_sensor)
    sensor_pk = models.IntegerField(blank=False, null=False)



class SensorBoolean(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    sensor_id = models.IntegerField(blank=False, null=False , default=0)
    label = models.CharField(blank=False, max_length=50)
    description = models.CharField(blank=True, max_length=200)
    value  = models.BooleanField(null=True)
    def __str__(self):
        return str(self.value)

class SensorInt(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    sensor_id = models.IntegerField(blank=False, null=False, default=0)
    label = models.CharField(blank=False, max_length=50)
    description = models.CharField(blank=True, max_length=200)
    value  = models.IntegerField(blank=True, null=True)
    def __str__(self):
        return str(self.value)

class SensorFloat(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    sensor_id = models.IntegerField(blank=False, null=False, default=0)
    label = models.CharField(blank=False, max_length=50)
    description = models.CharField(blank=True, max_length=200)
    value  = models.FloatField(blank=True, null=True)
    def __str__(self):
        return str(self.value)

class SensorLogger(models.Model):   #float only
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    sensor_id = models.IntegerField(blank=False, null=False, default=0)
    label = models.CharField(blank=False, max_length=50)
    description = models.CharField(blank=True, max_length=200)
    def __str__(self):
        return str(self.pk)

class LogEntry(models.Model):
    sensor = models.ForeignKey(SensorLogger, on_delete=models.CASCADE)
    value = models.FloatField(blank=True, null=True)
    timestamp = models.DateTimeField(blank=False, default=datetime.datetime.now)
    def __str__(self):
        return str(self.value)+' '+str(self.timestamp)
