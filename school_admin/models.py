from django.db import models
#Create your models here.

class Admin_used_count(models.Model):
    used_count = models.IntegerField(default=0)