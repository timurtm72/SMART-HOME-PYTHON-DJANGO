from rest_framework import generics, viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import *
from .serializers import *
from django.contrib.auth.models import User
from django.shortcuts import render

DEBUG_ON = 0

class MyDevices(APIView):
    def get(self, request):
        devices= Device.objects.filter(user=request.user)
        data = DeviceSerializer_public(devices, many=True).data
        return Response(data)

#'device_id','label','description','last_connection', 'number_of_sensors'
class AddDevice(APIView):
    def post(self, request):
        user=request.user.pk
        if DEBUG_ON == 1:
            print("user in AddDevice",user)
            print("description in AddDevice",request.data.get("description"))
            print("label in AddDevice", request.data.get("label"))
            print("device_id in AddDevice", request.data.get("device_id"))
            print("last_connection in AddDevice", request.data.get("last_connection"))
            print("number_of_sensors in AddDevice", request.data.get("number_of_sensors"))
        devices_per_user = DevicesPerUser.objects.filter(user=user)
        if DEBUG_ON == 1:
            print("devices_per_user in AddDevice is None",devices_per_user)
        if not devices_per_user.exists():
           devicePU = DevicesPerUser()
           devicePU.number_of_devices = 0
           devicePU.user_id = user
           devicePU.save()
           if DEBUG_ON == 1:
               print("devicePU.number_of_devices in AddDevice is save ", devicePU.number_of_devices)
               print(" devicePU.user_id in AddDevice is save ",  devicePU.user_id)
        devices_per_user = DevicesPerUser.objects.get(user=user)
        device_id =request.data.get("device_id")
        label = request.data.get("label")
        description = request.data.get("description")
        if label==None:
            return Response({"error": "must specify a label"}, status=status.HTTP_400_BAD_REQUEST)
        data={"user":user,"label":label, "device_id":device_id}
        if description !=None:
            data.update({"description":description,})
        serializer = DeviceSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            if DEBUG_ON == 1:
                print("devices_per_user QwerySet = ",devices_per_user)
            devices_per_user.number_of_devices+=1
            if DEBUG_ON == 1:
                print("devices_per_user.number_of_devices = ", devices_per_user.number_of_devices)
            devices_per_user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({"error": "incorrect data"}, status=status.HTTP_400_BAD_REQUEST)


class DeviceInfo(APIView):
    def get(self, request, device_id):
        user = request.user
        try:
            device = Device.objects.filter(user=user).get(device_id=device_id)
        except Device.DoesNotExist:
            return Response({"error": "The requested device does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        sensors_boolean =SensorBoolean.objects.filter(device=device)
        sensors_boolean_data = SensorBooleanSerializer(sensors_boolean, many=True).data

        sensors_int = SensorInt.objects.filter(device=device)
        sensors_int_data = SensorIntSerializer(sensors_int, many=True).data

        sensors_float = SensorFloat.objects.filter(device=device)
        sensors_float_data = SensorIntSerializer(sensors_float, many=True).data
        data= DeviceSerializer_public(device).data
        if(sensors_boolean_data!=[]):
            data.update({'boolean_sensors':sensors_boolean_data,})
        if(sensors_int_data!=[]):
            data.update({'int_sensors:':sensors_int_data,})
        if(sensors_float_data!=[]):
            data.update({'float_sensors:':sensors_float_data})
        return Response(data)


def borrarRegistro(tipo, sensor_pk):
    if tipo==1:
        SensorBoolean.objects.get(pk=sensor_pk).delete()
    elif tipo==2:
        SensorInt.objects.get(pk=sensor_pk).delete()
    elif tipo==3:
        SensorFloat.objects.get(pk=sensor_pk).delete()

from itertools import count
def firstMissingSince(sequence, start=1):
    uniques = set(sequence) # { x for x in sequence if x>=start }
    return next( x for x in count(start) if x not in uniques )

def nextAviableId(device):
    a=SensorIndex.objects.filter(device=device).values_list('sensor_id')
    l=[None]*len(a)
    cont=0
    for i in a:
        l[cont]=i[0]
        cont+=1
    return firstMissingSince(l)


class AddSensorBoolean(APIView):
    def post(self, request, device_id, sensor_id=None):
        user = request.user
        try:
            device = Device.objects.filter(user=user).get(device_id=device_id)
        except Device.DoesNotExist:
            return Response({"error": "The requested device does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        label = request.data.get("label")
        if label==None:
            return Response({"error": "must specify a label"}, status=status.HTTP_400_BAD_REQUEST)

        sensor_id_argument= True
        if sensor_id ==None:
            sensor_id = nextAviableId(device)
            sensor_id_argument= False

        data={"device":device.pk, "label":label, "sensor_id":sensor_id,}
        value = request.data.get("value")
        if value != None:
            data.update({"value":value})
        description = request.data.get("description")
        if description !=None:
            data.update({"description":description,})
        serializer=SensorBooleanSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            device.number_of_sensors+=1
            device.save()
            if sensor_id_argument:    #si le pase a sensor_id entre los argumentos
                try:                                              #si ya existia la posición a escribir
                    index= SensorIndex.objects.filter(device=device).get(sensor_id=sensor_id)
                    borrarRegistro(index.tipo, index.sensor_pk)  #borro el registro virjo
                    index.sensor_pk=serializer.data['id']         #actualizo la info en el index con el nuevo SensorBoolean
                    index.tipo=1
                    index.save()
                    device.number_of_sensors-=1   #quito el senor q había sumado a la cuenta
                    device.save()
                except SensorIndex.DoesNotExist:  #si no existia la posición a escribir
                    index=SensorIndex.objects.create(device=device,sensor_id=sensor_id, tipo=1, sensor_pk=serializer.data['id'])
                    index.save()
            else:
                index=SensorIndex.objects.create(device=device,sensor_id=sensor_id, tipo=1, sensor_pk=serializer.data['id'])
                index.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response({"error": "incorrect data"}, status=status.HTTP_400_BAD_REQUEST)


class AddSensorInt(APIView):
    def post(self, request, device_id, sensor_id=None):
        user = request.user
        try:
            device = Device.objects.filter(user=user).get(device_id=device_id)
        except Device.DoesNotExist:
            return Response({"error": "The requested device does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        label = request.data.get("label")
        if label==None:
            return Response({"error": "must specify a label"}, status=status.HTTP_400_BAD_REQUEST)

        sensor_id_argument= True
        if sensor_id ==None:
            sensor_id = nextAviableId(device)
            sensor_id_argument= False

        data={"device":device.pk, "label":label, "sensor_id":sensor_id,}
        value = request.data.get("value")
        if value != None:
            data.update({"value":value})
        description = request.data.get("description")
        if description !=None:
            data.update({"description":description,})
        serializer=SensorIntSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            device.number_of_sensors+=1
            device.save()
            if sensor_id_argument:    #si le pase a sensor_id entre los argumentos
                try:                                              #si ya existia la posición a escribir
                    index= SensorIndex.objects.filter(device=device).get(sensor_id=sensor_id)
                    borrarRegistro(index.tipo, index.sensor_pk)  #borro el registro virjo
                    index.sensor_pk=serializer.data['id']         #actualizo la info en el index con el nuevo SensorBoolean
                    index.tipo=2
                    index.save()
                    device.number_of_sensors-=1   #quito el senor q había sumado a la cuenta
                    device.save()
                except SensorIndex.DoesNotExist:  #si no existia la posición a escribir
                    index=SensorIndex.objects.create(device=device,sensor_id=sensor_id, tipo=2, sensor_pk=serializer.data['id'])
                    index.save()
            else:
                index=SensorIndex.objects.create(device=device,sensor_id=sensor_id, tipo=2, sensor_pk=serializer.data['id'])
                index.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response({"error": "incorrect data"}, status=status.HTTP_400_BAD_REQUEST)


class AddSensorFloat(APIView):
    def post(self, request, device_id, sensor_id=None):
        user = request.user
        try:
            device = Device.objects.filter(user=user).get(device_id=device_id)
        except Device.DoesNotExist:
            return Response({"error": "The requested device does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        label = request.data.get("label")
        if label==None:
            return Response({"error": "must specify a label"}, status=status.HTTP_400_BAD_REQUEST)

        sensor_id_argument= True
        if sensor_id ==None:
            sensor_id = nextAviableId(device)
            sensor_id_argument= False

        data={"device":device.pk, "label":label, "sensor_id":sensor_id,}
        value = request.data.get("value")
        if value != None:
            data.update({"value":value})
        description = request.data.get("description")
        if description !=None:
            data.update({"description":description,})
        serializer=SensorFloatSerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            device.number_of_sensors+=1
            device.save()
            if sensor_id_argument:    #si le pase a sensor_id entre los argumentos
                try:                                              #si ya existia la posición a escribir
                    index= SensorIndex.objects.filter(device=device).get(sensor_id=sensor_id)
                    borrarRegistro(index.tipo, index.sensor_pk)  #borro el registro virjo
                    index.sensor_pk=serializer.data['id']         #actualizo la info en el index con el nuevo SensorBoolean
                    index.tipo=3
                    index.save()
                    device.number_of_sensors-=1   #quito el senor q había sumado a la cuenta
                    device.save()
                except SensorIndex.DoesNotExist:  #si no existia la posición a escribir
                    index=SensorIndex.objects.create(device=device,sensor_id=sensor_id, tipo=3, sensor_pk=serializer.data['id'])
                    index.save()
            else:
                index=SensorIndex.objects.create(device=device,sensor_id=sensor_id, tipo=3, sensor_pk=serializer.data['id'])
                index.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response({"error": "incorrect data"}, status=status.HTTP_400_BAD_REQUEST)



class GetSensor(APIView):
    def get(self, request, device_id, sensor_id):
        user=request.user
        try:
            device = Device.objects.filter(user=user).get(device_id=device_id)
        except Device.DoesNotExist:
            return Response({"error": "The requested device does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            sensor_index = SensorIndex.objects.filter(device=device).get(sensor_id=sensor_id)
            tipo = sensor_index.tipo
            sensor_pk= sensor_index.sensor_pk
        except SensorIndex.DoesNotExist:
            return Response({"error": "The requested sensor does not exist in this device"}, status=status.HTTP_400_BAD_REQUEST)

        if (tipo==1):
            print(sensor_pk,sensor_id)
            sensor = SensorBoolean.objects.get(pk=sensor_pk)
            return Response(SensorBooleanSerializer(sensor).data)
        elif tipo ==2 :
            sensor = SensorInt.objects.get(pk=sensor_pk)
            return Response(SensorIntSerializer(sensor).data)
        elif tipo ==3:
            sensor = SensorFloat.objects.get(pk=sensor_pk)
            return Response(SensorFloatSerializer(sensor).data)
        else:
            return  Response({"error": "tipo de sensor desconcido"}, status=status.HTTP_400_BAD_REQUEST)


class GetSensorValue(APIView):
    def get(self, request, device_id, sensor_id):
        user=request.user
        try:
            device = Device.objects.filter(user=user).get(device_id=device_id)
        except Device.DoesNotExist:
            return Response({"error": "The requested device does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            sensor_index = SensorIndex.objects.filter(device=device).get(sensor_id=sensor_id)
            tipo = sensor_index.tipo
            sensor_pk= sensor_index.sensor_pk
        except SensorIndex.DoesNotExist:
            return Response({"error": "The requested sensor does not exist in this device"}, status=status.HTTP_400_BAD_REQUEST)

        if (tipo==1):
            sensor = SensorBoolean.objects.get(pk=sensor_pk)
            return Response(SensorBooleanSerializerValue(sensor).data)
        elif tipo ==2 :
            sensor = SensorInt.objects.get(pk=sensor_pk)
            return Response(SensorIntSerializerValue(sensor).data)
        elif tipo ==3:
            sensor = SensorFloat.objects.get(pk=sensor_pk)
            return Response(SensorFloatSerializerValue(sensor).data)
        else:
            return  Response({"error": "tipo de sensor desconcido"}, status=status.HTTP_400_BAD_REQUEST)


class SetSensorValue(APIView):
    def post(self, request, device_id, sensor_id):
        user=request.user
        try:
            device = Device.objects.filter(user=user).get(device_id=device_id)
        except Device.DoesNotExist:
            return Response({"error": "The requested device does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            sensor_index = SensorIndex.objects.filter(device=device).get(sensor_id=sensor_id)
            tipo = sensor_index.tipo
            sensor_pk= sensor_index.sensor_pk
        except SensorIndex.DoesNotExist:
            return Response({"error": "The requested sensor does not exist in this device"}, status=status.HTTP_400_BAD_REQUEST)

        value = request.data.get("value")
        if (tipo==1):
            sensor = SensorBoolean.objects.get(pk=sensor_pk)
            serializer = SensorBooleanSerializerValue(instance=sensor, data={'value':value})
        elif tipo ==2 :
            sensor = SensorInt.objects.get(pk=sensor_pk)
            serializer = SensorIntSerializerValue(instance=sensor, data={'value':value})
        elif tipo ==3:
            sensor = SensorFloat.objects.get(pk=sensor_pk)
            serializer = SensorFloatSerializerValue(instance=sensor, data={'value':value})
        else:
            return  Response({"error": "tipo de sensor desconcido"}, status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserCreate(generics.CreateAPIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserSerializer


from django.contrib.auth import authenticate
class LoginView(APIView):
    permission_classes = ()
    def post(self, request,):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            return Response({"token": user.auth_token.key})
        else:
            return Response({"error": "Wrong Credentials"}, status=status.HTTP_400_BAD_REQUEST)
