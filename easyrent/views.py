from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth.models import User
from easyrent.models import *
from datetime import datetime, timedelta
from django.core.paginator import Paginator
import pytz

import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings


def checkOtherRents(place, init, end):
	rents = Rent.objects.filter(place=place)
	for r in rents:
		r.init = r.init.replace(tzinfo=None)
		r.end = r.end.replace(tzinfo=None)
		if r.init < init and r.end > init:
			return r
		if r.init > init and r.init < end:
			return r
	return None


def home(request):
	request.session['numNotifications'] = None
	placesAux = Place.objects.all()
	places = []

	today = datetime.now()

	location = request.POST.get('location')
	initD = request.POST.get('initD')
	initH = request.POST.get('initH')
	endD = request.POST.get('endD')
	endH = request.POST.get('endH')
	distance = request.POST.get('distance')
	orderBy = request.POST.get('orderBy')

	if (not initD and endD) or (not endD and initD):
		initD = None
		endD = None

	if not orderBy:
		orderBy = 'distance'

	if location:
		lan, lon = get_coords(location)
		if not lan:
			lan, lon = get_coords('Madrid')
			messages.error(request, 'Invalid location.')
	else:
		lan, lon = get_coords('Madrid')

	request.session['location'] = location
	request.session['initD'] = initD
	request.session['initH'] = initH
	request.session['endD'] = endD
	request.session['endH'] = endH
	request.session['distance'] = distance

	if initD:
		init = datetime.strptime(initD + initH, "%Y-%m-%d%H")
		end = datetime.strptime(endD + endH, "%Y-%m-%d%H")
		print(init,end)

		if init < today :
			messages.error(request, "Don't pick past dates.")
			initD = None
			endD = None
		elif end <= init:
			initD = None
			endD = None
			messages.error(request, 'The init datetime must be previous to the end datetime')
		
	for p in placesAux:
		if initD:
			if checkOtherRents(p, init, end):
				continue
		place = {
			'id':p.id,
			'name':p.name,
			'completeAddress':p.completeAddress(),
			'capacity':p.capacity,
			'price':p.price,
			'rating':p.rating,
			'numberRatings':p.numberRatings,
			'user':User.objects.get(id=p.user.id),
			'distance':round(distanceAux((lan,lon),(p.lan,p.lon)),2),
			'image':p.image
		}
		if distance and (place['distance'] > float(distance)):
			continue
		
		places.append(place)

	places = sorted(places, key=lambda k: k[orderBy]) 
	if orderBy == 'rating':
		places.reverse()

	
	if request.user.is_authenticated:
		request.session['numNotifications'] = len(Notification.objects.filter(user=request.user, read=False))
		places = list(filter(lambda place: place['user'] != request.user, places))
		
	p = Paginator(places, 3)
	numPage = request.GET.get('page', 1)
	numPages = p.num_pages

	try:
		page = p.page(numPage)
	except:
		page = p.page(1)

	return render(request, 'home.html', {'places':page, 'today':today, 'numPages':numPages, 'numPage':numPage, 'session':request.session})


def valid_inputs(password, username, first_name='a', last_name='a'):
	return first_name.isalpha() and last_name.isalpha() and password.isalnum() and username.isalnum()

def register(request):
	if request.method == 'POST':
		first_name = request.POST.get('first_name')
		last_name = request.POST.get('last_name')
		password1 = request.POST.get('password1')
		password2 = request.POST.get('password2')
		username = request.POST.get('username')

		if valid_inputs(password1,first_name, last_name, username):
			if (len(User.objects.filter(username=username)) > 0):
				messages.error(request, 'A user with that username already exists.')
				return render(request, 'register.html', {'session':request.session})

			if password1 != password2:
				messages.error(request, 'The passwords are not the same.')
				return render(request, 'register.html', {'session':request.session})


			user = User(first_name=first_name, last_name=last_name, username=username)
			user.set_password(password1)
			user.save()

			message = 'Welcome '+user.first_name+' '+user.last_name+' to EasyRent.'
			Notification.objects.create(
			    user = user,
			    reserver = None,
			    rent = None,
			    text = message)

			messages.success(request, 'You have registered your account.')
			return home(request)
		else:
			messages.error(request, 'The form is not valid.')
			return render(request, 'register.html', {'session':request.session})
	else:
		return render(request, 'register.html', {'session':request.session})


def user_login(request):
	if request.method == 'POST':
		if request.user.is_authenticated:
			messages.error(request, 'You have already logged in.')
			return home(request)
		
		password = request.POST.get('password')
		username = request.POST.get('username')

		if valid_inputs(password, username):

			user = authenticate(username=username, password=password)

			if user:
				if user.is_active:
					login(request, user)
					messages.info(request, 'You have logged in.')
					request.session['numNotifications'] = len(Notification.objects.filter(user=request.user, read=False))
					return home(request)
				else:
					messages.error(request, 'Your account is disabled.')
					return render(request, 'login.html')
			else:
				messages.error(request, 'Incorrect username or password.')
				return render(request, 'login.html')
		else:
			messages.error(request, 'The form is not valid.')
			return render(request, 'login.html')
	else:
		return render(request, 'login.html')


@login_required
def user_logout(request):
    logout(request)
    messages.info(request, 'You have logged out.')

    return home(request)

@login_required
def profile(request):
	return render(request, 'profile.html', {'session':request.session})


@login_required
def editProfile(request):
	if request.user.is_authenticated:
		if request.method == 'POST':
			first_name = request.POST.get('first_name')
			last_name = request.POST.get('last_name')
			password = request.POST.get('password')
			username = request.POST.get('username')

			if valid_inputs(first_name=first_name, last_name=last_name, password='a', username=username):
				if request.user.username != username:
					if (len(User.objects.filter(username=username)) > 0):
						messages.error(request, 'A user with that username already exists.')
						return render(request, 'editProfile.html', {'session':request.session})

				user = User.objects.get(username=request.user.username)
				user.username = username
				user.first_name = first_name
				user.last_name = last_name

				user.save()
				
				message = 'You have edited your profile succesfully.'
				Notification.objects.create(
				    user = user,
				    reserver = None,
				    rent = None,
				    text = message)
				request.session['numNotifications'] = len(Notification.objects.filter(user=request.user, read=False))

				messages.success(request, 'You have edited your profile succesfully.')
				return home(request)
			else:
				messages.error(request, 'The form is not valid.')
				return render(request, 'editProfile.html', {'session':request.session})
		else:
			return render(request, 'editProfile.html', {'session':request.session})
	else:
		messages.error(request, 'You need to login to edit your profile.')
		return home(request)


@login_required
def changePassword(request):
	if request.user.is_authenticated:
		if request.method == 'POST':
			password1 = request.POST.get('password1')
			password2 = request.POST.get('password2')

			if valid_inputs(first_name='a', last_name='a', password=password1, username='a'):
				if password1 != password2:
					messages.error(request, 'The passwords are not the same.')
					return render(request, 'changePassword.html', {'session':request.session})

				user = User.objects.get(username=request.user.username)
				user.set_password(password1)
				user.save()

				message = 'You have changed your password.'
				Notification.objects.create(
				    user = user,
				    reserver = None,
				    rent = None,
				    text = message)
				request.session['numNotifications'] = len(Notification.objects.filter(user=request.user, read=False))


				messages.success(request, 'You have changed your password.')
				return user_login(request)
			else:
				messages.error(request, 'The form is not valid.')
				return render(request, 'editProfile.html', {'session':request.session})
		else:
			return render(request, 'changePassword.html', {'session':request.session})
	else:
		messages.error(request, 'You need to login to change your password.')
		return home(request)


@login_required
def addPlace(request):
	if request.user.is_authenticated:
		if request.method == 'POST':
			name = request.POST.get('name')
			country = request.POST.get('country')
			province = request.POST.get('province')
			cp = request.POST.get('cp')
			address = request.POST.get('address')
			capacity = int(request.POST.get('capacity'))
			price = float(request.POST.get('price'))
			image = request.FILES.get('image')

			aux = 'place' + str(len(Place.objects.all())) + '.jpg'
			default_storage.save(settings.MEDIA_ROOT + '/imagesPlaces/' + aux, ContentFile(image.read()))
			path = 'images/imagesPlaces/' + aux
			try:
				Place.objects.create(
					name=name,
					user=request.user,
					country=country,
					province=province,
					cp=cp,
					address=address,
					capacity=capacity,
					price=price,
					image=path)

				message = 'You have created the place '+name
				Notification.objects.create(
				    user = request.user,
				    reserver = None,
				    rent = None,
				    text = message)
				request.session['numNotifications'] = len(Notification.objects.filter(user=request.user, read=False))

				messages.success(request, 'Your place have been created.')
				return myPlaces(request)
			except:
				messages.error(request, 'Invalid address. Couldnt create your place.')
				return render(request, 'addPlace.html', {'session':request.session})

		else:
			return render(request, 'addPlace.html', {'session':request.session})
	else:
		messages.error(request, 'You need to login to add new places.')
		return home(request)


@login_required
def editPlace(request, idPlace):
	if request.user.is_authenticated:
		place = Place.objects.get(id=idPlace)
		
		if request.method == 'POST':
			name = request.POST.get('name')
			country = request.POST.get('country')
			province = request.POST.get('province')
			cp = request.POST.get('cp')
			address = request.POST.get('address')
			capacity = int(request.POST.get('capacity'))
			price = float(request.POST.get('price'))
			image = request.FILES.get('image')

			if image:
				default_storage.delete(settings.STATIC_DIR + '/' + place.image)
				default_storage.save(settings.STATIC_DIR + '/' + place.image, ContentFile(image.read()))

			place.name = name
			place.country = country
			place.province = province
			place.cp = cp
			place.address = address
			place.capacity = capacity
			place.price = price

			try:
				place.save()
				message = 'You have edited your place '+place.name
				Notification.objects.create(
				    user = request.user,
				    reserver = None,
				    rent = None,
				    text = message)
				request.session['numNotifications'] = len(Notification.objects.filter(user=request.user, read=False))

				messages.success(request, 'Your place have been changed.')
				return myPlaces(request)
			except:
				messages.error(request, 'Invalid address. Couldnt create your place.')
				return render(request, 'editPlace.html', {'place':place, 'session':request.session})

		else:
			return render(request, 'editPlace.html', {'place':place, 'session':request.session})
	else:
		messages.error(request, 'You need to login to add new places.')
		return home(request)



def updateRating(place, rate):
	if place.numberRatings == 0:
		place.rating = rate
	else:	
		newRate = ((place.rating * place.numberRatings) + rate)/(place.numberRatings + 1)
		place.rating = newRate
	place.numberRatings += 1
	place.save()
	return

@login_required
def ratePlace(request, idRent):
	if request.user.is_authenticated:
		rent = Rent.objects.get(id=idRent)
		place = rent.place
		
		if rent.rated:
			messages.error(request, 'You have already rated the place.')
			return myRents(request)

		if request.method == 'POST':
			rate = request.POST.get('rate')
			updateRating(place, rate)

			rent.rated = True
			rent.save()
			
			message = 'You have rated the place '+place.name+' with a rate of '+rate
			Notification.objects.create(
				user = request.user,
				reserver = None,
				rent = None,
				text = message)
			request.session['numNotifications'] = len(Notification.objects.filter(user=request.user, read=False))


			messages.success(request, 'You have rated the place.')
			return myRents(request)
		else:
			return render(request, 'ratePlace.html', {'rent':rent, 'place': rent.place, 'session':request.session})
	else:
		messages.error(request, 'You need to login to rate places.')
		return home(request)


def checkOtherRents(place, init, end):
	rents = Rent.objects.filter(place=place)
	for r in rents:
		r.init = r.init.replace(tzinfo=None)
		r.end = r.end.replace(tzinfo=None)
		if r.init < init and r.end > init:
			return r
		if r.init > init and r.init < end:
			return r
	return None


def summary(request, idPlace):
	if request.user.is_authenticated:
		place = Place.objects.get(id=idPlace)
		today = datetime.now()
		
		firstDate = request.POST.get('firstDate')
		lastDate = request.POST.get('lastDate')
		start = request.POST.get('start')
		end = request.POST.get('end')

		init = datetime.strptime(firstDate + start, "%Y-%m-%d%H")
		end = datetime.strptime(lastDate + end, "%Y-%m-%d%H")
		if init < today:
			messages.error(request, 'You cant rent a place before today.')
			return render(request, 'rentPlace.html', {'place':place, 'today':today, 'session':request.session})
		if end <= init:
			messages.error(request, 'The start of the rent must be previous to the end of the rent')
			return render(request, 'rentPlace.html', {'place':place, 'today':today, 'session':request.session})
		
		r = checkOtherRents(place, init, end)
		if r:
			messages.error(request, 'This place is already rented from ' + str(r.init) + ' to ' + str(r.end) + '. Try to rent it at other times.')
			return render(request, 'rentPlace.html', {'place':place, 'today':today, 'session':request.session})
			

		rent = Rent.objects.create(
			place=place,
			user=request.user,
			init=init,
			end=end
			)


		return render(request, 'summary.html', {'place':place, 'rent':rent, 'session':request.session})

def rentPlace(request, idPlace):
	if request.user.is_authenticated:
		place = Place.objects.get(id=idPlace)
		today = datetime.now()
		
		return render(request, 'rentPlace.html', {'place':place, 'today':today, 'session':request.session})
	else:
		messages.error(request, 'You need to login to rent a place.')
		return home(request)


@login_required
def deletePlace(request, idPlace):
	if request.user.is_authenticated:
		place = Place.objects.get(id=idPlace)
		if place.user != request.user:
			messages.error(request, 'You cant delete a place which is not yours.')
			return home(request)
		name = place.name
		place.delete()
		message = 'You have deleted your place '+name
		Notification.objects.create(
		    user = request.user,
		    reserver = None,
		    rent = None,
		    text = message)
		request.session['numNotifications'] = len(Notification.objects.filter(user=request.user, read=False))

		messages.success(request, 'You have deleted your place.')
		return myPlaces(request)
	else:
		messages.error(request, 'You need to login to add new places.')
		return home(request)


@login_required
def confirmRent(request, idRent, deny=False):
	if request.user.is_authenticated:
		rent = Rent.objects.get(id=idRent)
		if deny:
			rent.delete()
			messages.success(request, 'You have denied the rent.')
			return home(request)
		else:
			message = ('User ' + request.user.username + ' has rented your place ' +
				rent.place.name + ' from ' + str(rent.init.date()) + ' at ' + str(rent.init.time()) + ' to ' + str(rent.end.date()) + ' at ' + str(rent.end.time()))
			noti = Notification.objects.create(
			    user = rent.place.user,
			    reserver = request.user,
			    rent = rent,
			    text = message)
			message = 'You have rented the place '+rent.place.name
			Notification.objects.create(
			    user = request.user,
			    reserver = None,
			    rent = None,
			    text = message)
			request.session['numNotifications'] = len(Notification.objects.filter(user=request.user, read=False))

			messages.success(request, 'The rent has been confirmed.')
			return myRents(request)
	else:
		messages.error(request, 'You need to login to confirm rents.')
		return home(request)

@login_required
def editRent(request, idRent):
	rent = Rent.objects.get(id=idRent)
	if request.method == 'POST':

		today = datetime.now()
		
		firstDate = request.POST.get('firstDate')
		lastDate = request.POST.get('lastDate')
		start = request.POST.get('start')
		end = request.POST.get('end')

		init = datetime.strptime(firstDate + start, "%Y-%m-%d%H")
		end = datetime.strptime(lastDate + end, "%Y-%m-%d%H")
		if init <= today:
			messages.error(request, 'You cant rent a place before today.')
			return render(request, 'editRent.html', {'place':place, 'today':today, 'session':request.session})
		if end <= init:
			messages.error(request, 'The start of the rent must be previous to the end of the rent')
			return render(request, 'editRent.html', {'place':place, 'today':today, 'session':request.session})
		
		message = ('User ' + request.user.username + ' has requested a rent change in the place ' + rent.place.name +
			' from ' + str(init.date()) + ' at '  + str(init.time()) + ' to ' + str(end.date()) + ' at ' + str(end.time()))

		noti = Notification.objects.create(
			user = rent.place.user,
			reserver = request.user,
			rent = rent,
			confirmType = True,
			text = message,
			newInit = init,
			newEnd = end)

		messages.success(request, 'The edit of the rent has been notificated to the owner.')
		return myRents(request)
	else:
		return render(request, 'editRent.html', {'place': rent.place, 'rent':rent, 'session':request.session})


@login_required
def cancelRent(request, idRent):
	rent = Rent.objects.get(id=idRent)
	today = datetime.now()
	tomorrow = today.date() + timedelta(days=1)
	if (rent.init.date() < tomorrow):
		messages.error(request, "You can't cancel a rent that starts in less than 24 hours.")
		return myRents(request)
	elif (rent.init.date() == tomorrow) and (rent.init.time() < today.time()):
		messages.error(request, "You can't cancel a rent that starts in less than 24 hours.")
		return myRents(request)

	message = ('User ' + request.user.username + ' has canceled his rent in your place ' + rent.place.name +
		' from ' + str(rent.init.date()) + ' at '  + str(rent.init.time()) + ' to ' + str(rent.end.date()) + ' at ' + str(rent.end.time()))
	name = rent.place.name
	rent.delete()
	noti = Notification.objects.create(
		user = rent.place.user,
		reserver = request.user,
		rent = None,
		text = message,)
	message = 'You have canceled your rent in the place '+name
	Notification.objects.create(
	    user = request.user,
	    reserver = None,
	    rent = None,
	    text = message)
	request.session['numNotifications'] = len(Notification.objects.filter(user=request.user, read=False))

	messages.success(request, 'You have canceled your rent.')
	return myRents(request)


@login_required
def myPlaces(request):
	if request.user.is_authenticated:
		places = Place.objects.filter(user=request.user)
		return render(request, 'myPlaces.html', {'places':places, 'session':request.session})
	else:
		messages.error(request, 'You need to login to see your places.')
		return home(request)


@login_required
def myRents(request):
	if request.user.is_authenticated:
		rents = Rent.objects.filter(user=request.user)
		rentsType = []
		today = pytz.utc.localize(datetime.now())
		for r in rents:
			if r.init > today:
				typeR = 0
			else:
				if r.end > today:
					typeR = 1
				else:
					typeR = 2
			rent = {
				'id':r.id,
				'place':r.place,
				'user':r.user,
				'init':r.init,
				'end':r.end,
				'type':typeR,
				'rated':r.rated,
				'numberHours':r.numberHours(),
				'totalPrice':r.totalPrice(),
				}
			rentsType.append(rent)

		return render(request, 'myRents.html', {'rents':rentsType, 'session':request.session})
	else:
		messages.error(request, 'You need to login to see your rents.')
		return home(request)

@login_required
def notifications(request):
	if request.user.is_authenticated:
		notifications = Notification.objects.filter(user=request.user)
		return render(request, 'notifications.html', {'notifications':notifications, 'session':request.session})
	else:
		messages.error(request, 'You need to login to see your notifications.')
		return home(request)

@login_required
def readNotification(request, idNotification):
	if request.user.is_authenticated:
		notification = Notification.objects.get(id=idNotification)
		notification.read = True
		notification.save()

		request.session['numNotifications'] = len(Notification.objects.filter(user=request.user, read=False))

		return notifications(request)
	else:
		messages.error(request, 'You need to log in to read notifications.')
		return home(request)


@login_required
def aproveNotification(request, idNotification):
	if request.user.is_authenticated:
		notification = Notification.objects.get(id=idNotification)
		notification.read = True
		notification.save()


		notification.rent.init = notification.newInit
		notification.rent.end = notification.newEnd
		notification.rent.save()

		Notification.objects.create(
			user = notification.reserver,
			reserver = request.user,
			rent = notification.rent,
			text = 'User ' + request.user.username + ' has accepted your rent change in the place ' + notification.rent.place.name)
		
		request.session['numNotifications'] = len(Notification.objects.filter(user=request.user, read=False))

		messages.success(request, 'You have accepted the request of the rent change.')
		return notifications(request)
	else:
		messages.error(request, 'You need to log in to aprove notifications.')
		return home(request)


@login_required
def denyNotification(request, idNotification):
	if request.user.is_authenticated:
		notification = Notification.objects.get(id=idNotification)
		notification.read = True
		notification.save()

		Notification.objects.create(
			user = notification.reserver,
			reserver = request.user,
			rent = notification.rent,
			text = 'User ' + request.user.username + ' has denied your rent change in the place ' + rent.place.name)
		
		request.session['numNotifications'] = len(Notification.objects.filter(user=request.user, read=False))

		messages.success(request, 'You have denied the request of the rent change.')
		return notifications(request)
	else:
		messages.error(request, 'You need to log in to deny notifications.')
		return home(request)
