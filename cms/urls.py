from django.urls import path
from .views import *

urlpatterns = [
    
    path("hotel-login/", HotelLoginFetch.as_view(), name="hotel_login"),

# -------------------- INDEX --------------------
    
     path("",index,name='index'),

# -------------------- DASHBOARD --------------------
    path("dashboard/",dashboard,name='dashboard'),
# -------------------- HOTEL REGISTER --------------------

     path("register/", hotel_register, name="hotel_register"),

     
# -------------------- HOTEL AUTHENTICATION AND HOTEL DETAILS --------------------


     path('login/',login_view,name='login_view'),
     path('results/', hotel_results_page, name='hotel_result'),
     path("manual-booking/", manual_booking, name="manual_booking"),
]
     
    
