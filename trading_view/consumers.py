import json
from asgiref.sync import async_to_sync

from django.core import serializers
from .models import *
import decimal 
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict
from channels.generic.websocket import WebsocketConsumer, JsonWebsocketConsumer
# from channels.backends.base import WebsocketConsumer #WebsocketConsumer
from datetime import datetime, date, time
from django.http import JsonResponse
from rest_framework import serializers

class Buyserializers(serializers.ModelSerializer):
    class Meta:
        model = Stock_Data
        fields = ('__all__')

class Sellserializers(serializers.ModelSerializer):
    class Meta:
        model = Stock_Data
        fields = ('__all__')
    
class Strategyserializers(serializers.ModelSerializer):
    class Meta:
        model = Strategy
        fields = ('__all__')


class Stockinfoserializer(serializers.ModelSerializer):
    strategy = Strategyserializers(read_only = True)
    buy = Buyserializers(read_only = True)
    sell = Sellserializers(read_only = True)
    class Meta:
      model = StockInfo
      fields = ('__all__')
    
    

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        print(o)
        if isinstance(o, datetime):
            return str(o)
        if isinstance(o, decimal.Decimal):
            return float(o)
        # Any other serializer if needed
        return super(CustomJSONEncoder, self).default(o)
class ChatConsumer(JsonWebsocketConsumer):
    model_instance = StockInfo.objects.all()
    serializer = Stockinfoserializer(model_instance, many=True)
       

    def connect(self):
        async_to_sync(self.channel_layer.group_add)(
            'events',
            self.channel_name
        )
        self.accept()
        self.send_json({
            'type': 'events.alarm',
            'data': self.serializer.data
    })

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        print(text_data)
        self.send_json({"type": "test"})     
       
    def events_alarm(self, event):
        self.send_json(
            {
                'type': 'events.alarm',
                'data': event['content']
            }
        )