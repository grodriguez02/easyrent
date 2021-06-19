from django.test import TestCase
from django.test import Client

from django.contrib.auth.models import User
from easyrent.models import *
from easyrent.management.commands.populate import Command

from easyrentproyect.settings import BASE_DIR
pathToProject = BASE_DIR


class ExampleTest(TestCase):
	def test_example01(self):
		"this test is OK"
		self.assertEqual(0, 0,
			"Error: 0 not equal to 0")

		self.assertIsNotNone(1,
			"Error: 1 is None")

	def test_example02(self):
		"this test will fail"

		self.assertFalse(True, 
			"Error: this test will fail because True is not False")
