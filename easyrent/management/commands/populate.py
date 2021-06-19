from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from django.conf import settings

import django

django.setup()

from easyrent.models import *

class Command(BaseCommand):
    help = 'populate db'

    def handle(self, *args, **options):
        self.cleanDatabase()
        self.createSuperUser()
        self.addUsers()
        self.addPlaces()
        self.addRents()
        self.addNotifications()
    
    def cleanDatabase(self):
        for user in User.objects.all():
            user.delete();

        for place in Place.objects.all():
            place.delete();

        for rent in Rent.objects.all():
            rent.delete();

        for notification in Notification.objects.all():
            notification.delete();
    
    def createSuperUser(self):
        User.objects.create_superuser('guilleadmin', 'a@a.es', 'guilleadmin')


    def addUsers(self):
        user = User(
          first_name = 'Guillermo',
          last_name = 'Rodriguez',
          username = 'guille')
        user.set_password('guille')
        user.save()

        user = User(
          first_name = 'Juan',
          last_name = 'Perez',
          username = 'juan')
        user.set_password('juan')
        user.save()

        user = User(
          first_name = 'Rosa',
          last_name = 'Martin',
          username = 'rosa')
        user.set_password('rosa')
        user.save()

        user = User(
          first_name = 'Irene',
          last_name = 'Lopez',
          username = 'irene')
        user.set_password('irene')
        user.save()

    def addPlaces(self):
        place = Place(
          name = 'Cristaleras Sol',
          user = User.objects.get(username='guille'),
          country = 'España',
          province = 'Madrid',
          cp = '28013',
          address = 'Puerta del Sol 7',
          capacity = 6,
          price = 6.5,
          image='images/imagesPlaces/local1.jpg')
        place.save()

        place = Place(
          name = 'Pequeño local barato Alcobendas',
          user = User.objects.get(username='irene'),
          country = 'España',
          province = 'Madrid',
          cp = '28100',
          address = 'Calle del Marqués de la Valdavia 111',
          capacity = 8,
          price = 5.5,
          image='images/imagesPlaces/local2.jpg')
        place.save()

        place = Place(
          name = 'Local amplio en Preciados',
          user = User.objects.get(username='guille'),
          country = 'España',
          province = 'Madrid',
          cp = '28013',
          address = 'Calle Preciados 4',
          capacity = 13,
          price = 6,
          image='images/imagesPlaces/local3.jpg')
        place.save()

        place = Place(
          name = 'Local cerca del acueducto',
          user = User.objects.get(username='juan'),
          country = 'España',
          province = 'Segovia',
          cp = '40001',
          address = 'Plaza Azoguejo 1',
          capacity = 10,
          price = 5.5,
          image='images/imagesPlaces/local4.jpg')
        place.save()

    def addRents(self):
        #creamos un alquiler pasado
        rent = Rent(
          place = Place.objects.all()[1],
          user = User.objects.get(username='guille'),
          init = datetime(2021,1,1,0,0),
          end = datetime(2021,1,1,12,0)
        )
        rent.save()

        #creamos un alquiler presente
        rent = Rent(
          place = Place.objects.all()[3],
          user = User.objects.get(username='guille'),
          init = datetime.now(),
          end = datetime.now() + timedelta(days=1)
        )
        rent.save()

    def addNotifications(self):
        notification = Notification(
          user = User.objects.get(username='guille'),
          reserver = User.objects.get(username='irene'),
          rent = Rent.objects.all()[0],
          confirmType = True,
          text ='Texto de prueba',
          newInit = datetime(2022,1,1,10,0),
          newEnd = datetime(2022,1,1,12,0),
          date = datetime(2021,1,1,12,0),
        )
        notification.save()

        notification = Notification(
          user = User.objects.get(username='guille'),
          reserver = None,
          rent = None,
          confirmType = False,
          text ='Texto de prueba 2',
          newInit = None,
          newEnd = None,
          date = datetime(2021,1,1,12,0),
        )
        notification.save()

        notification = Notification(
          user = User.objects.get(username='guille'),
          reserver = None,
          rent = None,
          read=True,
          confirmType = False,
          text ='Texto de prueba 3',
          newInit = None,
          newEnd = None,
          date = datetime(2021,1,1,12,0),
        )
        notification.save()
