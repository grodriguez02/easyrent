from django.test import TestCase
from django.test import Client

from django.contrib.auth.models import User
from easyrent.models import *
from easyrent.management.commands.populate import Command

from easyrentproyect.settings import BASE_DIR
pathToProject = BASE_DIR


class ModelTests(TestCase):

	def setUp(self):
		self.client = Client()

		# load Command class from populate
		c = Command()

		# execute populate
		c.handle()
		

	def test_users(self):
		print("\nTesting Users...")
		_dict = {}
		_dict[0] = {
			'first_name': 'Guillermo',
			'last_name': 'Rodriguez',
			'username': 'guille'}
		_dict[1] = {
			'first_name': 'Juan',
			'last_name': 'Perez',
			'username': 'juan'}
		_dict[2] = {
			'first_name': 'Rosa',
			'last_name': 'Martin',
			'username': 'rosa'}
		_dict[3] = {
			'first_name': 'Irene',
			'last_name': 'Lopez',
			'username': 'irene'}
		_dict[4] = {
			'first_name': None,
			'last_name': None,
			'username': 'guilleadmin'}
		
		users = User.objects

		self.assertEqual(len(users.all()), len(_dict),
			"Error: wrong number of users")

		for u in _dict:
			u = _dict[u]
			if u['username'] == 'guilleadmin':
				self.assertIsNotNone(users.get(username=u['username']))
			else:
				self.assertIsNotNone(users.get(
					username=u['username'], first_name=u['first_name'], last_name=u['last_name']))


	def test_places(self):
		print("\nTesting Places...")
		_dict = {}
		_dict[0] = {
			'name': 'Cristaleras Sol',
			'user': User.objects.get(username='guille'),
			'country': 'España',
			'province': 'Madrid',
			'cp': '28013',
			'address': 'Puerta del Sol 7',
			'capacity': 6,
			'price': 6.5}
		_dict[1] = {
			'name': 'Pequeño local barato Alcobendas',
			'user': User.objects.get(username='irene'),
			'country': 'España',
			'province': 'Madrid',
			'cp': '28100',
			'address': 'Calle del Marqués de la Valdavia 111',
			'capacity': 8,
			'price': 5.5}
		_dict[2] = {
			'name': 'Local amplio en Preciados',
			'user': User.objects.get(username='guille'),
			'country': 'España',
			'province': 'Madrid',
			'cp': '28013',
			'address': 'Calle Preciados 4',
			'capacity': 13,
			'price': 6}
		_dict[3] = {
			'name': 'Local cerca del acueducto',
			'user': User.objects.get(username='juan'),
			'country': 'España',
			'province': 'Segovia',
			'cp': '40001',
			'address': 'Plaza Azoguejo 1',
			'capacity': 10,
			'price': 5.5}

		places = Place.objects

		self.assertEqual(len(places.all()), len(_dict),
			"Error: wrong number of places")

		for p in _dict:
			p = _dict[p]
			self.assertIsNotNone(places.get(
				name=p['name'], user=p['user'], country=p['country'], province=p['province'],
				cp=p['cp'], address=p['address'], capacity=p['capacity'], price=p['price']))


	

	def test_rents(self):
		print("\nTesting Rents...")
		_dict = {}
		_dict[0] = {
			'place': Place.objects.all()[1],
			'user': User.objects.get(username='guille')}
		_dict[1] = {
			'place': Place.objects.all()[3],
			'user': User.objects.get(username='guille')}

		rents = Rent.objects

		self.assertEqual(len(rents.all()), len(_dict),
			"Error: wrong number of rents")

		for r in _dict:
			r = _dict[r]
			self.assertIsNotNone(rents.get(
				place=r['place'], user=r['user']))


	

	def test_notifications(self):
		print("\nTesting Notifications...")
		_dict = {}
		_dict[0] = {
			'user': User.objects.get(username='guille'),
			'reserver': User.objects.get(username='irene'),
			'rent': Rent.objects.all()[0],
			'read': False,
			'confirmType': True,
			'text': 'Texto de prueba',
			'newInit': datetime(2022,1,1,10,0),
			'newEnd': datetime(2022,1,1,12,0),
			'date': datetime(2021,1,1,12,0)
			}
		_dict[1] = {
			'user': User.objects.get(username='guille'),
			'reserver': None,
			'rent': None,
			'read': False,
			'confirmType': False,
			'text': 'Texto de prueba 2',
			'newInit': None,
			'newEnd': None,
			'date': datetime(2021,1,1,12,0)
			}
		_dict[2] = {
			'user': User.objects.get(username='guille'),
			'reserver': None,
			'rent': None,
			'read': True,
			'confirmType': False,
			'text': 'Texto de prueba 3',
			'newInit': None,
			'newEnd': None,
			'date': datetime(2021,1,1,12,0)
			}

		notifications = Notification.objects

		self.assertEqual(len(notifications.all()), len(_dict),
			"Error: wrong number of notification")

		for n in _dict:
			n = _dict[n]
			self.assertIsNotNone(notifications.get(
				user=n['user'], reserver=n['reserver'], rent=n['rent'],
				read=n['read'], confirmType=n['confirmType'], text=n['text']))