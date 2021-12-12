import decimal
from datetime import date
from json import dumps

import yaml
from asgiref.sync import async_to_sync
from channels import layers
from channels.layers import get_channel_layer
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.http.response import HttpResponse
from django.shortcuts import render

from trading_view.consumers import Stockinfoserializer

from .models import *
# Create your views here.
def home(request):
    stockdata = StockInfo.objects.all()
    return render(request, 'trading_view/index.html', {"StockInfos": stockdata})

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def data(request, *args, **kwargs):
    if request.method == "POST":
        data = request.body.decode("utf-8")
        print(r'{}'.format(data))
        
        dict_data=yaml.full_load(r"{}".format(data))
        if dict_data["strategy"]["order_action"] == "buy":

            # buy model
            brk = float(dict_data["strategy"]["order_price"])*0.01  
            nrate = float(dict_data["strategy"]["order_price"]) + brk
            amt = nrate*float(dict_data["strategy"]["order_contracts"])
            buy_model  = Stock_Data.objects.create(
                time_frame=dict_data["timeframe"], 
                stockname=dict_data["ticker"], 
                quanty=dict_data["strategy"]["order_contracts"], 
                price = dict_data["strategy"]["order_price"], 
                brk = brk, nrate = nrate, amt = amt
                )

            strategy=Strategy.objects.filter(name = dict_data["strategy_name"]).first()

            stockinfo = StockInfo.objects.filter(strategy=strategy)
            stockinfo = stockinfo.filter(buy = None)
            stockinfo = stockinfo.filter(sell__time_frame=dict_data["timeframe"], sell__stockname = dict_data["ticker"], sell__quanty=dict_data["strategy"]["order_contracts"])
            stockinfo = stockinfo.first()
            if stockinfo:
                stockinfo.buy = buy_model
                total = stockinfo.sell.amt - amt
                stockinfo.total = total
                stockinfo.save()
                print("Updating model")
            else:
                strategy, created = Strategy.objects.get_or_create(name=dict_data["strategy_name"])
                stockinfo = StockInfo.objects.create(strategy=strategy, buy = buy_model )
                print("Saving model")
            print(stockinfo)
        elif dict_data["strategy"]["order_action"] == "sell":

            # buy model
            brk = float(dict_data["strategy"]["order_price"])*0.01
            nrate = float(dict_data["strategy"]["order_price"]) - brk
            amt = nrate*float(dict_data["strategy"]["order_contracts"])
            sell_model  = Stock_Data.objects.create(
                time_frame=dict_data["timeframe"], 
                stockname=dict_data["ticker"], 
                quanty= -dict_data["strategy"]["order_contracts"], 
                price = dict_data["strategy"]["order_price"], 
                brk = brk, nrate = nrate, amt = amt
                )

            strategy=Strategy.objects.filter(name = dict_data["strategy_name"]).first()
            stockinfo = StockInfo.objects.filter(strategy=strategy)
            stockinfo = stockinfo.filter(sell = None)
            stockinfo = stockinfo.filter(buy__time_frame=dict_data["timeframe"], buy__stockname = dict_data["ticker"], buy__quanty=dict_data["strategy"]["order_contracts"])
            stockinfo = stockinfo.first()
            if stockinfo:
                stockinfo.sell = sell_model
                total = amt - stockinfo.buy.amt  
                stockinfo.total = total
                stockinfo.save()
                print("Updateing model")
            else:
                strategy, created = Strategy.objects.get_or_create(name=dict_data["strategy_name"])
                stockinfo = StockInfo.objects.create(strategy=strategy, sell = sell_model )
                print("Saving model")
            print(stockinfo)
        model_instance = StockInfo.objects.all()

        serializer = Stockinfoserializer(model_instance, many=True)
        layer = get_channel_layer()
        async_to_sync(layer.group_send)('events', {
        'type': 'events.alarm',
        'content': serializer.data
            })
        return render(request, 'trading_view/main.html', {"StockInfos": StockInfo.objects.all()})
    else:
        return render(request, 'trading_view/main.html', {"StockInfos": StockInfo.objects.all()})



'''

{
    "strategy_name": "EMA test",
    "timeframe": S,
    "passphrase": "somelongstring123",
    "time": "2021-12-03T13:34:17Z",
    "exchange": "BITSTAMP",
    "ticker": "BTCUSD",
    "bar": {
        "time": "2021-12-03T13:34:17Z",
        "open": 57451.06,
        "high": 57451.06,
        "low": 57451.06,
        "close": 57451.06,
        "volume": 0.1085
    },
    "strategy": {
        "market_position": "flat",
        "market_position_size": 0,
        "prev_market_position": "long",
        "prev_market_position_size": 0.017746
    }
}

'''

# Strategy_Name
# Buy	
# Time_FRAME
# TIME	DATE	STOCK_NAME
# Buy_QTY
# Buy_Price
# Buy_BRK
# Buy_NRATE
# Buy_AMT
# Sell	Time_FRAME
# TIME	DATE	STOCK_NAME
# Sell_QTY
# Sell_Price
# Sell_BRK
# Sell_NRATE
# Sell_AMT
