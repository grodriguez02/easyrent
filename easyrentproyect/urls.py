from django.contrib import admin
from django.urls import path
from easyrent import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
	path('admin/', admin.site.urls),
	path('', views.home),
	path('home/', views.home, name='home'),
	path('register/', views.register, name='register'),
	path('login/', views.user_login, name='login'),
	path('logout/', views.user_logout, name='logout'),
	path('profile/', views.profile, name='profile'),
	path('editProfile/', views.editProfile, name='editProfile'),
	path('changePassword/', views.changePassword, name='changePassword'),
	path('addPlace/', views.addPlace, name='addPlace'),
	path('editPlace/<idPlace>/', views.editPlace, name='editPlace'),
	path('ratePlace/<idRent>/', views.ratePlace, name='ratePlace'),
	path('rentPlace/<idPlace>/', views.rentPlace, name='rentPlace'),
	path('summary/<idPlace>/', views.summary, name='summary'),
	path('confirmRent/<idRent>/<deny>/', views.confirmRent, name='confirmRent'),
	path('confirmRent/<idRent>/', views.confirmRent, name='confirmRent'),
	path('editRent/<idRent>/', views.editRent, name='editRent'),
	path('cancelRent/<idRent>/', views.cancelRent, name='cancelRent'),
	path('deletePlace/<idPlace>/', views.deletePlace, name='deletePlace'),
	path('myPlaces/', views.myPlaces, name='myPlaces'),
	path('myRents/', views.myRents, name='myRents'),
	path('notifications/', views.notifications, name='notifications'),
	path('readNotification/<idNotification>/', views.readNotification, name='readNotification'),
	path('aproveNotification/<idNotification>/', views.aproveNotification, name='aproveNotification'),
	path('denyNotification/<idNotification>/', views.denyNotification, name='denyNotification'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)