from django.urls import path
from .views import *

urlpatterns = [
    
    path("hotel-login/", HotelLoginFetch.as_view(), name="hotel_login"),



# -------------------- HOTEL AUTHENTICATION AND HOTEL DETAILS --------------------


    path("",login_view,name='login_view'),
     path('results/', hotel_results_page, name='hotel_result'),
    
]