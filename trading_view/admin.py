from django.contrib import admin
from .models import Stock_Data, StockInfo, Strategy
# Register your models here.


admin.site.register(StockInfo)
admin.site.register(Stock_Data)
admin.site.register(Strategy)