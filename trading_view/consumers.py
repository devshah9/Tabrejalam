import json
from asgiref.sync import async_to_sync

from django.core import serializers
from django.db.models.fields import PositiveIntegerRelDbTypeMixin
from .models import *
import decimal 
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict
from channels.generic.websocket import WebsocketConsumer, JsonWebsocketConsumer
# from channels.backends.base import WebsocketConsumer #WebsocketConsumer
from datetime import datetime, date, time
from django.http import JsonResponse
from .serializers import *    

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
       

    def connect(self):
        async_to_sync(self.channel_layer.group_add)(
            'events',
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        receive_data = json.loads(text_data)
        strategy_instance = Strategy.objects.all()
        model_instance = StockInfo.objects.all()
        if receive_data["url_param"] != {'strategy': {}, 'date': {}}:
            print(receive_data["url_param"])
            if receive_data["url_param"]["strategy"]:
                model_instance = model_instance.filter(strategy__name =receive_data["url_param"]["strategy"] )
                print(receive_data["url_param"]["strategy"])
            if receive_data["url_param"]["date"]:
                date_range = receive_data["url_param"]["date"].split('-')
                date0 = datetime.strptime(date_range[0], "%m/%d/%Y")
                date1 = datetime.strptime(date_range[1], "%m/%d/%Y")
                date0 =date0.strftime("%Y-%m-%d")
                date1 =date1.strftime("%Y-%m-%d")
                model_instance = model_instance.filter(buy__date__range =[date0, date1])
                print(model_instance)
        else:
            model_instance = StockInfo.objects.all()
        serializer = Stockinfoserializer(model_instance, many=True)
        strategyserializers = Strategyserializers(strategy_instance, many=True) 
        self.send_json({
            'type': 'events.alarm',
            'data': serializer.data,
            'strategy': strategyserializers.data, 
    })
    def events_alarm(self, event):
        # print(event["content"])
        # receive_data = json.loads(text_data)
        model_instance = StockInfo.objects.all()
        serializer = Stockinfoserializer(model_instance, many=True)
        
        self.send_json(
            {
                'type': 'events.alarm',
                'data': serializer.data
            }
        )

