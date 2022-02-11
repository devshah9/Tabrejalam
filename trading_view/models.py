from os import times
from django.db import models
from django.db.models.fields import CharField
from django.db.models.fields.related import ForeignKey

# Create your models here.
class Strategy(models.Model):
    name = CharField(max_length=40, unique=True)

class Stock_Data(models.Model):
    time        = models.TimeField(auto_now=True)
    time_frame  = models.CharField(max_length=120)
    date        = models.DateField(auto_now_add=True)
    stockname   = models.CharField(max_length=120)
    quanty      = models.FloatField()
    price       = models.FloatField()
    brk         = models.FloatField()
    nrate       = models.FloatField()
    amt         = models.FloatField()




class StockInfo(models.Model):
    strategy    = models.ForeignKey(Strategy, on_delete=models.CASCADE)
    buy         = models.OneToOneField(Stock_Data, on_delete=models.CASCADE, null=True, blank=True, related_name="stock_buy_info")
    sell        = models.OneToOneField(Stock_Data, on_delete=models.CASCADE, null=True, blank=True, related_name="stock_sell_info")
    total       = models.FloatField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.buy != None and self.sell != None and self.total == None:
            self.total = (self.buy.amt + self.sell.amt) * -1
            print('this is from save method ', self.buy.amt, self.sell.amt)
        super(StockInfo, self).save(*args, **kwargs)