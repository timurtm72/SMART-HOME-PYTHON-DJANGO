from django.urls import path
from .views import *

urlpatterns = [
    path('device/', MyDevices.as_view(), name='my_devices'),               #list of all your devices
    path('device/add/',AddDevice.as_view(), name='add_device' ),
    path('device/<int:device_id>/',DeviceInfo.as_view(), name='device_info' ), #list of every sensor of specific device

    path('device/<int:device_id>/add_sensor_boolean/', AddSensorBoolean.as_view(), name='add_sensor_boolean'),
    path('device/<int:device_id>/add_sensor_boolean/<int:sensor_id>/', AddSensorBoolean.as_view(), name='add_sensor_boolean'),

    path('device/<int:device_id>/add_sensor_int/', AddSensorInt.as_view(), name='add_sensor_int'),
    path('device/<int:device_id>/add_sensor_int/<int:sensor_id>/', AddSensorInt.as_view(), name='add_sensor_int'),

    path('device/<int:device_id>/add_sensor_float/', AddSensorFloat.as_view(), name='add_sensor_float'),
    path('device/<int:device_id>/add_sensor_float/<int:sensor_id>/', AddSensorFloat.as_view(), name='add_sensor_float'),

    path('device/<int:device_id>/sensor/<int:sensor_id>/',GetSensor.as_view(), name='get_sensor_value'),
    path('device/<int:device_id>/sensor/<int:sensor_id>/value/',GetSensorValue.as_view(), name='get_sensor_value'),
    path('device/<int:device_id>/sensor/<int:sensor_id>/set/', SetSensorValue.as_view(), name='set_sensor_value'),

    path("login/", LoginView.as_view(), name="login"),
    path("users/", UserCreate.as_view(), name="user_create"),
]
