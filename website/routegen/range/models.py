from django.db import models

# Create your models here.
class airport(models.Model):
    a_name = models.CharField(max_length=128)
    a_city = models.CharField(max_length=64)
    a_country = models.CharField(max_length=64)
    a_iata = models.CharField(length=3)
