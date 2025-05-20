from django.db import models
from school.models import *
#Create your models here.
class Admin_detail(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, null=True, related_name='batch')
    name = models.CharField(max_length=100, null=True)
    mobile = models.IntegerField(null=True)
    pin =models.CharField(max_length=10, null=True)
    qualification = models.CharField(max_length=200, null=True)
    image = models.ImageField(upload_to="admin_images",default="",null=True, blank=True)
    about_us = models.CharField(max_length=1000, null=True)
    status = models.IntegerField(default=1, null=True)
    
class Admin_used_count(models.Model):
    used_count = models.IntegerField(default=0)