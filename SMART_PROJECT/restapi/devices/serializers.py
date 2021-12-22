from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *
from rest_framework.authtoken.models import Token


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields ='__all__'
        extra_kwargs = {'pk': {'write_only': True}}   #this prevents pk to be shown back in the response

class DevicesPerUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = DevicesPerUser
        fields ='__all__'

class DeviceSerializer_public(serializers.ModelSerializer):
    class Meta:
        model = Device
        fields =('device_id','label','description','last_connection', 'number_of_sensors')


class SensorBooleanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorBoolean
        fields = '__all__'# ('pk','label','value',)
        extra_kwargs = {'pk': {'write_only': True}}

class SensorBooleanSerializerValue(serializers.ModelSerializer):
    class Meta:
        model = SensorBoolean
        fields = ('value',)


class SensorIntSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorInt
        fields = '__all__'# ('pk','label','value',)
        extra_kwargs = {'pk': {'write_only': True}}

class SensorIntSerializerValue(serializers.ModelSerializer):
    class Meta:
        model = SensorInt
        fields = ('value',)


class SensorFloatSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorFloat
        fields =  '__all__'# ('pk','label','value',)
        extra_kwargs = {'pk': {'write_only': True}}

class SensorFloatSerializerValue(serializers.ModelSerializer):
    class Meta:
        model = SensorFloat
        fields =  ('value',)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        token = Token.objects.create(user=user)
        token.save()
        return user
