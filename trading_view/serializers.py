from .models import *
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

