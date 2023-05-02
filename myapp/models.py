from django.db import models


class Brands(models.Model):
    code = models.CharField(max_length=8)
    name = models.CharField(max_length=30)
    division = models.CharField(max_length=20)

    def __str__(self):
        return '【' + self.code + '】' + self.name
