from django.urls import path
from .views import *

urlpatterns = [
    


# -------------------- INDEX --------------------
    
     path("",index,name='index'),

# -------------------- CONNECTIONS --------------------

  
  path("connect/",connect_website,name="connect_website"),

  
# -------------------- DASHBOARD --------------------
    path("dashboard/",dashboard,name='dashboard'),
# -------------------- HOTEL REGISTER --------------------

     path("register/", hotel_register, name="hotel_register"),

     
# -------------------- HOTEL AUTHENTICATION AND HOTEL DETAILS --------------------


     path('login/',login_view,name='login_view'),
     path('results/', hotel_results_page, name='hotel_result'),
     path("manual-booking/", manual_booking, name="manual_booking"),
     # -------------------- Booking --------------------
     path("all-bookings/", all_bookings, name="all_bookings"),
     path("cancel-booking/",cancel_booking,name="cancel_booking"),
]
     
    
