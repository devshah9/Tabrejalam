import yaml
import json
from datetime import datetime
from urllib import request

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from django.contrib.auth.models import Group, User
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from rest_framework import permissions, viewsets

from .models import *
from .serializers import *

from trading_view.consumers import Stockinfoserializer

# Create your views here.
def home(request):
    stockdata = StockInfo.objects.all()
    return render(request, 'trading_view/index.html', {"StockInfos": stockdata})



@csrf_exempt
def data(request, *args, **kwargs):
    if request.method == "POST":
        data = request.body.decode("utf-8")
        
        dict_data=yaml.full_load(r"{}".format(data))
        print(dict_data)
        if dict_data["strategy"]["order_action"] == "buy":

            # buy model
            print("Making a buy model")
            brk = float(dict_data["strategy"]["order_price"])*0.0001  
            nrate = float(dict_data["strategy"]["order_price"]) + brk
            amt = nrate*float(dict_data["strategy"]["order_contracts"])
            buy_model  = Stock_Data.objects.create(
                time_frame=dict_data["timeframe"], 
                stockname=dict_data["ticker"], 
                quanty=dict_data["strategy"]["order_contracts"], 
                price = dict_data["strategy"]["order_price"], 
                brk = brk, nrate = nrate, amt = amt
                )
            print("Made a buy model", buy_model)
            
            # Finding Corrosponding 
            print("Finding Corrosponding")
            strategy=Strategy.objects.get_or_create(name = dict_data["strategy_name"])[0]
            stockinfo = StockInfo.objects.filter(strategy=strategy)
            stockinfo = stockinfo.filter(buy = None)
            stockinfo = stockinfo.filter(sell__time_frame=dict_data["timeframe"], sell__stockname = dict_data["ticker"])
            stockinfo = stockinfo.first()

            print("Done Finding")
            # If it has corrosponding and it is a close position 
            if stockinfo and str(dict_data["strategy"]["order_id"]).startswith("LONG"):
                print("Found and i am in closing positing right now", stockinfo)
                # Getting Corrosponding data
                sell = Stock_Data.objects.get(id=stockinfo.sell.id)
                print(sell.quanty, -dict_data["strategy"]["order_contracts"], sell.quanty < -dict_data["strategy"]["order_contracts"])
                if sell.quanty < -dict_data["strategy"]["order_contracts"]: 
                    print("We have more stock quanity and selling some")
                    # Changing old sell
                    previous_quanty = -sell.quanty
                    sell.quanty = -dict_data["strategy"]["order_contracts"]
                    sell.amt = sell.nrate*sell.quanty
                    print(49, sell.amt)
                    sell.save()
                    print("Stockdata Updated", sell)
                    stockinfo.sell = sell
                    stockinfo.save()
                    print("stockinfo saved", stockinfo)
                    
                    # Creating new sell
                    new_quanty = previous_quanty - dict_data["strategy"]["order_contracts"]
                    amt = nrate*new_quanty
                    new_sell = Stock_Data.objects.create(
                        time        = sell.time,
                        time_frame  = sell.time_frame,
                        date        = sell.date,
                        stockname   = sell.stockname,
                        quanty      = -new_quanty,
                        price       = sell.price,
                        brk         = sell.brk,
                        nrate       = sell.nrate,
                        amt         = -amt 
                        )
                    print("Stock_Data for sell has been created", new_sell)
                    StockInfo.objects.create(strategy = strategy, sell = new_sell)
                    print("new StockInfo has been created")
                stockinfo.buy = buy_model
                stockinfo.save()
                print("stockinfo updated", stockinfo)
            elif str(dict_data["strategy"]["order_id"]).startswith("LONG"):
                # strategy, created = Strategy.objects.get_or_create(name=dict_data["strategy_name"])
                stockinfo = StockInfo.objects.create(strategy=strategy, buy = buy_model )
                print("Saving model", stockinfo)
            # print(stockinfo)
        elif dict_data["strategy"]["order_action"] == "sell":

            # sell model
            print("make a sell model")
            brk = float(dict_data["strategy"]["order_price"])*0.0001
            nrate = float(dict_data["strategy"]["order_price"]) - brk
            amt = nrate*float(dict_data["strategy"]["order_contracts"])
            sell_model  = Stock_Data.objects.create(
                time_frame=dict_data["timeframe"], 
                stockname=dict_data["ticker"], 
                quanty= -dict_data["strategy"]["order_contracts"], 
                price = dict_data["strategy"]["order_price"], 
                brk = brk, nrate = nrate, amt = -amt
                )
            print("Made a sell model", sell_model)

            # Finding Corrosponding 
            strategy=Strategy.objects.get_or_create(name = dict_data["strategy_name"])[0]
            stockinfo = StockInfo.objects.filter(strategy=strategy)
            stockinfo = stockinfo.filter(sell = None)
            stockinfo = stockinfo.filter(buy__time_frame=dict_data["timeframe"], buy__stockname = dict_data["ticker"])
            stockinfo = stockinfo.first()

            print("Done Finding")
            # If it has corrosponding and it is a close position 
            if stockinfo and str(dict_data["strategy"]["order_id"]).startswith("SHORT"):
                print("Found and i am in closing positing right now", stockinfo)
                # Getting Corrosponding data
                buy = Stock_Data.objects.get(id=stockinfo.buy.id)
                print(buy.quanty, dict_data["strategy"]["order_contracts"], buy.quanty > dict_data["strategy"]["order_contracts"])
                if buy.quanty > dict_data["strategy"]["order_contracts"]:
                    print("We have selled more stock quanity and buy some")
                    # Changing old buy 
                    previous_quanty = buy.quanty
                    buy.quanty = dict_data["strategy"]["order_contracts"]
                    buy.amt = buy.nrate*buy.quanty
                    print(100, buy.amt)
                    buy.save()
                    print("Stockdata Updated", buy)
                    stockinfo.buy = buy
                    stockinfo.save()
                    print("stockinfo saved", stockinfo)
                    
                    # Creating new buy
                    new_quanty = previous_quanty - dict_data["strategy"]["order_contracts"]
                    amt = nrate*new_quanty
                    new_buy = Stock_Data.objects.create(
                        time        = buy.time,
                        time_frame  = buy.time_frame,
                        date        = buy.date,
                        stockname   = buy.stockname,
                        quanty      = new_quanty,
                        price       = buy.price,
                        brk         = buy.brk,
                        nrate       = buy.nrate,
                        amt         = amt 
                        )
                    print("Stock_Data for sell has been created", new_buy)
                    StockInfo.objects.create(strategy=strategy, buy = new_buy )        
                    print("new StockInfo has been created")
                stockinfo.sell = sell_model
                stockinfo.save()
                print("stockinfo updated", stockinfo)
                # total = amt - stockinfo.buy.amt  
                # stockinfo.total = total
                print("Updateing model")
            elif str(dict_data["strategy"]["order_id"]).startswith("SHORT"):
                # strategy, created = Strategy.objects.get_or_create(name=dict_data["strategy_name"])
                stockinfo = StockInfo.objects.create(strategy=strategy, sell = sell_model )
                print("Saving model", stockinfo)
            # print(stockinfo)
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





class StrategyViewSet(viewsets.ModelViewSet):
    queryset = Strategy.objects.all()
    serializer_class = Strategyserializers


class TradeAllViewSet(viewsets.ModelViewSet):
    queryset = StockInfo.objects.all()
    serializer_class = Stockinfoserializer

class TradeByViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        queryset = StockInfo.objects.all()

        if self.request.query_params.get('toDate'):
            date = self.request.query_params.get('toDate') 
            splited_date = str(date).split("-") 
            year, month, date = int(splited_date[0]), int(splited_date[1]), int(splited_date[2])
            queryset = queryset.filter(
                Q(buy__date__lte = datetime(year, month, date)) |
                Q(sell__date__lte = datetime(year, month, date)))
        if self.request.query_params.get('fromDate'):
            date = self.request.query_params.get('fromDate') 
            splited_date = str(date).split("-") 
            year, month, date = int(splited_date[0]), int(splited_date[1]), int(splited_date[2])
            queryset = queryset.filter(
                Q(buy__date__gte = datetime(year, month, date)) |
                Q(sell__date__gte = datetime(year, month, date)))
        if self.request.query_params.get('strategyName'):
            strategy_name = self.request.query_params.get('strategyName')
            queryset = queryset.filter(strategy__name = strategy_name)
        if self.request.query_params.get('stockName'):
            stockname = self.request.query_params.get('stockName')
            queryset = queryset.filter(buy__name = stockname)
        return queryset
    serializer_class = Stockinfoserializer


def StockAllViewSet(request, *args, **kwargs):
    dic = {}
    a = StockInfo.objects.values('sell__stockname').distinct().annotate(Count('sell__stockname'))
    for i in a:
        if i['sell__stockname']:
            print(235, i)
            dic[i['sell__stockname']] = i['sell__stockname__count']
    a = StockInfo.objects.values('buy__stockname').distinct().annotate(Count('buy__stockname'))
    for i in a:
        if i["buy__stockname"]:
            print(240, i)
            if i["buy__stockname"] in dic:
                if dic[i['buy__stockname']] < i['buy__stockname__count']:
                    dic[i['buy__stockname']] = i['buy__stockname__count']
            else:
                dic[i['buy__stockname']] = i['buy__stockname__count']

    json_data = json.dumps(dic)
    
    return HttpResponse(json_data, content_type='application/json')



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
