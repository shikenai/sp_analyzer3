from django.db import models
from django.utils import timezone

class Brands(models.Model):
    code = models.CharField(max_length=8)
    name = models.CharField(max_length=30)
    division = models.CharField(max_length=20)
    is_holding = models.BooleanField(verbose_name='保有', blank=True, null=True)
    is_watching = models.BooleanField(verbose_name='監視', blank=True, null=True)

    def __str__(self):
        return '【' + self.code + '】' + self.name


class Judge(models.Model):
    brand = models.ForeignKey(to=Brands, on_delete=models.CASCADE)
    date = models.DateField()
    trend = models.CharField(max_length=5)
    judge = models.TextField()
    created_at = models.DateTimeField(default=timezone.now())

    def __str__(self):
        return '【' + self.brand.code + ' ' + self.brand.name + '】' + self.date.strftime("%Y年%m月%d日")

class Trades(models.Model):
    brand = models.ForeignKey(to=Brands, on_delete=models.CASCADE)
    Date = models.DateField(blank=True, null=True)
    Close = models.FloatField(verbose_name='終値', blank=True, null=True)
    High = models.FloatField(verbose_name='高値', blank=True, null=True)
    Low = models.FloatField(verbose_name='安値', blank=True, null=True)
    Open = models.FloatField(verbose_name='始値', blank=True, null=True)
    Volume = models.FloatField(verbose_name='出来高', blank=True, null=True)

    def __str__(self):
        return f'{self.brand} {self.Date.strftime("%Y年%m月%d日")}'
