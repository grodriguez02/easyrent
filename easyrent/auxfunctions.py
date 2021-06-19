from geopy.geocoders import Nominatim
from geopy.exc import GeopyError
import math

def get_coords(saddress):
	try:
		geolocator = Nominatim(user_agent="altaruru_testgeopy")
		location = geolocator.geocode(saddress)
		return location.latitude, location.longitude
	except:
		return None, None

def get_address(lan, lon):
	try:
		geolocator = Nominatim(user_agent="altaruru_testgeopy")
		scoord = ("%s %s" % (lan, lon))
		location = geolocator.reverse(scoord)
		return location.address
	except:		
		return None	

def distanceAux(p1, p2):
	R = 6373.0
	lat1 = math.radians(p1[0])
	lon1 = math.radians(p1[1])
	lat2 = math.radians(p2[0])
	lon2 = math.radians(p2[1])
	dlon = lon2 - lon1
	dlat = lat2 - lat1
	a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
	c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
	return R * c


