from django.contrib import admin
from easyrent.models import *
from django.contrib.auth.models import User


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'first_name', 'last_name')

class PlaceAdmin(admin.ModelAdmin):
    list_display =  ('name', 'user', 'country', 'province', 'cp', 'address', 'price', 'capacity', 'lan', 'lon')


class RentAdmin(admin.ModelAdmin):
    list_display = ('place', 'user', 'init', 'end')


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'reserver', 'rent', 'read', 'confirmType', 'text', 'newInit', 'newEnd')

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.register(Place, PlaceAdmin)
admin.site.register(Rent, RentAdmin)
admin.site.register(Notification, NotificationAdmin)