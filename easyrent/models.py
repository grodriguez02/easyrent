from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from easyrent.auxfunctions import *

from datetime import datetime, timedelta


class Place(models.Model):
	name = models.CharField(max_length=128)
	user = models.ForeignKey(User,on_delete=models.CASCADE)
	country = models.CharField(max_length=128)
	province = models.CharField(max_length=128)
	cp = models.CharField(max_length=5)
	address = models.CharField(max_length=128)
	capacity = models.IntegerField(default=0)
	price = models.FloatField(default=0)
	rating = models.FloatField(default=0)
	numberRatings = models.IntegerField(default=0)

	image = models.CharField(max_length=128)#path

	lan = models.FloatField(default=0)
	lon = models.FloatField(default=0)
	
	def completeAddress(self):
		return '%s, %s, %s, %s ' % (self.address, self.cp, self.province, self.country)
	
	def save(self, *args, **kwargs):
		self.lan, self.lon = get_coords(self.completeAddress())
		if not self.lan:
			raise ValueError

		super().save(*args, **kwargs)

	def __str__(self):
		return self.name


class Rent(models.Model):
    place = models.ForeignKey(Place,on_delete=models.CASCADE)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    init = models.DateTimeField(default=None)
    end = models.DateTimeField(default=None)
    rated = models.BooleanField(default=False)

    def __str__(self):
        return str(self.place) + ', by ' + str(self.user)
    
    def totalPrice(self):
        return self.numberHours() * self.place.price

    def numberHours(self):
    	diference = self.end - self.init
    	return int(diference.days * 24 + diference.seconds/3600)


class Notification(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    reserver = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reserver')
    rent = models.ForeignKey(Rent, on_delete=models.SET_NULL, null=True)
    read = models.BooleanField(default=False)
    confirmType = models.BooleanField(default=False)
    text = models.CharField(max_length=512)
    newInit = models.DateTimeField(default=None, null=True)
    newEnd = models.DateTimeField(default=None, null=True)

    date = models.DateTimeField(default=None, null=True)

    def save(self, *args, **kwargs):
        self.date = datetime.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.id) + str(self.user) + str(self.reserver) 
