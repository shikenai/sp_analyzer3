from django.contrib import admin
from myapp import models
# Register your models here.


admin.site.register(models.Brands)
admin.site.register(models.Trades)
admin.site.register(models.Judge)