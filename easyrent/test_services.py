from django.test import Client, TestCase
from django.urls import reverse

from easyrent.management.commands.populate import Command
from django.contrib.auth.models import User
from easyrent.models import *


USER_SESSION_ID = "_auth_user_id"


class ServiceTests(TestCase):
    def setUp(self):
        self.client1 = self.client
        self.client2 = Client()
        self.client3 = Client()
        self.populate = Command()
        self.populate.handle()


        self.user1 = User.objects.get(username='guille')
        self.paramsUser1 = {
            'username': self.user1.username,
            'first_name': self.user1.first_name,
            'last_name': self.user1.last_name,
            'password': self.user1.username,
        }

        self.user2 = User.objects.get(username='irene')
        self.paramsUser2 = {
            'username': self.user2.username,
            'first_name': self.user2.first_name,
            'last_name': self.user2.last_name,
            'password': self.user2.username,
        }

        self.user3 = User.objects.get(username='juan')
        self.paramsUser3 = {
            'username': self.user3.username,
            'first_name': self.user3.first_name,
            'last_name': self.user3.last_name,
            'password': self.user3.username,
        }

    def tearDown(self):
        self.populate.cleanDatabase()

    @classmethod
    def decode(cls, txt):
        return txt.decode("utf-8")

    @classmethod
    def loginTestUser(cls, client, user):
        client.force_login(user)

    def validate_response(self, title, response):
        self.assertRegex(self.decode(response.content), title)
        

    def test01_log_page(self):
        "log page response by login service"
        
        # check that no student is loged in
        self.assertFalse(self.client1.session.get(USER_SESSION_ID, False))

        # call "login" service and check that "Login" is in the title
        response = self.client1.get(reverse('login'), follow=True)
        self.assertEqual(response.status_code, 200)
        
        # but we have not login so no user should be active
        self.assertFalse(self.client1.session.get(USER_SESSION_ID, False))
        
        # check that the string "Login" is shown in the html response
        self.validate_response('Login', response)

    
    def test02_log_in(self):
        "login service"

        # no user logged in
        self.assertFalse(self.client1.session.get(USER_SESSION_ID, False))
        
        # log in
        self.client1.post(reverse('login'), self.paramsUser1, follow=True)

        # check user logged in
        self.assertTrue(self.client1.session.get(USER_SESSION_ID, False))
    
    def test03_log_out(self):
        "logout service"

        # no user logged in
        self.assertFalse(self.client1.session.get(USER_SESSION_ID, False))
        
        # log in
        self.client1.post(reverse('login'), self.paramsUser1, follow=True)

        # check user logged in
        self.assertTrue(self.client1.session.get(USER_SESSION_ID, False))

        # log out
        self.client1.post(reverse('logout'), follow=True)

        # user has logged out
        self.assertFalse(self.client1.session.get(USER_SESSION_ID, False))

    def test04_register_page(self):
        "register page response by register service"
        
        # check that no student is loged in
        self.assertFalse(self.client1.session.get(USER_SESSION_ID, False))

        # call "register" service and check that "Register" is in the title
        response = self.client1.get(reverse('register'), follow=True)
        self.assertEqual(response.status_code, 200)
        
        # check that the string "Register" is shown in the html response
        self.validate_response('Register', response)


    def test05_register_service(self):
        "register service"

        data = {
            'first_name': 'prueba',
            'last_name': 'prueba',
            'username': 'prueba',
            'password1': 'prueba',
            'password2': 'prueba',
            }
            
        num_users = len(User.objects.all())

        # register with valid params
        response = self.client1.post(reverse('register'), data, follow=True)

        # check that the string "You have registered your account" is shown in the html response
        self.validate_response('You have registered your account', response)

        # check that the number of users in de database has incrimented by 1
        self.assertEqual(num_users+1, len(User.objects.all()))

    def test06_register_service_wrong(self):
        "register service with username already registered and wrong parameters"

        data = {
            'first_name': 'prueba',
            'last_name': 'prueba',
            'username': 'guille',
            'password1': 'prueba',
            'password2': 'prueba',
            }
            
        num_users = len(User.objects.all())

        # register with an username already registered
        response = self.client1.post(reverse('register'), data, follow=True)
        self.validate_response('A user with that username already exists', response)
        self.assertEqual(num_users, len(User.objects.all()))

        data['username'] = 'prueba06'
        data['password2'] = 'prueba06'

        response = self.client1.post(reverse('register'), data, follow=True)
        self.validate_response('The form is not valid', response)
        self.assertEqual(num_users, len(User.objects.all()))

    def test07_place_pages(self):
        "add page, edit place, my places response by register service"
        
        response = self.client1.get(reverse('addPlace'), follow=True)
        # check cant access add place page without login
        self.assertEqual(response.status_code, 404)

        response = self.client1.get(reverse('editPlace', kwargs={'idPlace':1}), follow=True)
        # check cant access edit place page without login
        self.assertEqual(response.status_code, 404)

        response = self.client1.get(reverse('myPlaces'), follow=True)
        # check cant access my places page without login
        self.assertEqual(response.status_code, 404)
        
        self.loginTestUser(self.client1, self.user1)
        # call services and check that responses are ok
        response = self.client1.get(reverse('addPlace'), follow=True)
        self.assertEqual(response.status_code, 200)
        # check that the string "Add Place" is shown in the html response
        self.validate_response('Add Place', response)

        p = Place.objects.create(
            name = 'prueba',
            user = self.user1,
            country = 'España',
            province = 'Madrid',
            cp = '28013',
            address = 'Calle Preciados 4',
            image = 'prueba')

        response = self.client1.get(reverse('editPlace', kwargs={'idPlace':p.id}), follow=True)
        self.assertEqual(response.status_code, 200)
        # check that the string "Edit Place" is shown in the html response
        self.validate_response('Edit Place', response)

        response = self.client1.get(reverse('myPlaces'), follow=True)
        self.assertEqual(response.status_code, 200)
        # check that the string "My Places" is shown in the html response
        self.validate_response('My Places', response)

    def test09_edit_place(self):
        "test edit place service"
        
        # create the place with the user who wants to access the service
        place = Place.objects.create(
            name = 'prueba',
            user = self.user1,
            country = 'España',
            province = 'Madrid',
            cp = '28013',
            address = 'Calle Preciados 4',
            image = 'prueba')

        # call editPlace service with GET method
        response = self.client1.get(reverse('editPlace', kwargs={'idPlace':place.id}), follow=True)
        # check that the page cannot be accessed without logging in
        self.assertEqual(response.status_code, 404)

        # login
        self.loginTestUser(self.client1, self.user1)
        # call editPlace service with GET method 
        response = self.client1.get(reverse('editPlace', kwargs={'idPlace':place.id}), follow=True)
        # check that the page can be accessed when you have logged in
        self.assertEqual(response.status_code, 200)
        # check that the string "Edit Place" is shown in the html response
        self.validate_response('Edit Place', response)

        # now check that user cannot edit a place with invalid address (wrong address)
        data = {
            'name': 'prueba09',
            'country': 'España',
            'province': 'Madrid',
            'cp': '28013',
            'address': 'Random address 4',
            'capacity': 5,
            'price': 5.5,
            'image': 'prueba'
        }
        # call editPlace service with POST method and the new data 
        response = self.client1.post(reverse('editPlace', kwargs={'idPlace':place.id}), data, follow=True)
        self.assertEqual(response.status_code, 200)
        # check that the error message is shown in the html response
        self.validate_response('Invalid address. Couldnt create your place.', response)
        # update the place from database  
        place = Place.objects.get(id=place.id)  
        # check that place has not been edited            
        self.assertEqual(place.address, 'Calle Preciados 4')

        # now check that user can edit a place with valid address
        data = {
            'name': 'prueba09',
            'country': 'España',
            'province': 'Madrid',
            'cp': '28013',
            'address': 'Calle Preciados 3',
            'capacity': 5,
            'price': 5.5,
            'image': 'prueba'
        }
        # call editPlace service with POST method and the new data 
        response = self.client1.post(reverse('editPlace', kwargs={'idPlace':place.id}), data, follow=True)
        self.assertEqual(response.status_code, 200)
        # check that the success message is shown in the html response
        self.validate_response('Your place have been changed.', response)
        # update the place from database  
        place = Place.objects.get(id=place.id)  
        # check that place has been edited succesfully (address number was 4 instead of 3)           
        self.assertEqual(place.address, 'Calle Preciados 3')

