import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import redirect,render
from django.contrib import messages
from .serializers import RegisterSerializers
from .models import Register

# -------------------- Hotel Fetch API View --------------------

class HotelLoginFetch(APIView):

    def post(self, request):

        hotel_name = request.data.get("name")

        websites = [
            {
                "name": "Booking.com",
                "url": "https://project-demo-11.onrender.com/bookingapp/api/",
                "api_key": "9f8a7c6b5d4e3f2a1b0c"
            },
            {
                "name":"Bookmyhotel",
                "url":"https://bookmyhotel-5.onrender.com/bookingapp/api",
                "api_key":"a7c4e9d2f6b1c8e3d5f0a9b7c6d4e2f1"
            },
            {    
                "name":"Quickstayhub",
                "url":"https://quickstayhub-2.onrender.com/bookingapp/api",
                "api_key":"b9d2f4c7a1e8d3f6c5a0b7e9d1c4f2a8"
            },
            {    
                "name":"Homestay",
                "url":"https://homestay-1-4xmm.onrender.com/bookingapp/api",
                "api_key":"c7e2a4d9f1b8c6a3d5e0f2b7a9c4d1e8"
            },
             {    
                "name":"veedu",
                "url":"https://veedu.onrender.com/bookingapp/api",
                "api_key":"c1a7f9d4b6e3a8c2d5f0b1e7c9a4d2f6"
            },
        ]

        result = []

        for site in websites:

            headers = {
                "API-KEY": site["api_key"]
            }

            try:
                response = requests.get(site["url"], headers=headers,timeout=5)
                
                if response.status_code != 200:
                    continue

                try:
                    data = response.json()
                except:
                    continue

                hotels = data if isinstance(data, list) else data.get("results", [])

                for hotel in hotels:
                    if hotel["name"].lower() == hotel_name.lower():

                        result.append({
                            "website": site["name"],
                            "hotel_data": hotel
                        })

            except requests.exceptions.RequestException:
                continue

        return Response({
            "hotel": hotel_name,
            "websites_found": result
        })
# -------------------- INDEX --------------------

def index(request):
    return render(request,'index.html')


# -------------------- HOTEL REGISTER --------------------



def hotel_register(request):

    if request.method == "POST":

        hotel_name = request.POST.get("hotel_name")
        owner_name = request.POST.get("owner_name")
        email = request.POST.get("email")
        address = request.POST.get("address")
        city = request.POST.get("city")
        password = request.POST.get("password")

        Register.objects.create(
            hotel_name=hotel_name,
            owner_name=owner_name,
            email=email,
            address=address,
            city=city,
            password=password
        )

        return redirect("index")

    return render(request, "hotel_result.html")


# -------------------- HOTEL AUTHENTICATION AND HOTEL DETAILS --------------------



def login_view(request):

    if request.method == "POST":

        hotel_name = request.POST.get("hotel_name")
        password = request.POST.get("password")

        try:
            hotel = Register.objects.get(
                hotel_name=hotel_name,
                password=password
            )

            request.session["hotel_name"] = hotel.hotel_name

            return redirect("hotel_result")

        except Register.DoesNotExist:

            messages.error(request, "Invalid hotel name or password")
            return redirect("index")

    return redirect("index")






def hotel_results_page(request):
    hotel_name = request.session.get('hotel_name')
    if not hotel_name:
        return redirect('hotel_login')

    websites = [
        {"name": "Booking.com", "url": "https://project-demo-11.onrender.com/bookingapp/api/", "api_key": "9f8a7c6b5d4e3f2a1b0c"},
        {"name": "Bookmyhotel", "url": "https://bookmyhotel-5.onrender.com/bookingapp/api/", "api_key": "a7c4e9d2f6b1c8e3d5f0a9b7c6d4e2f1"},
        {"name": "Quickstayhub", "url": "https://quickstayhub-2.onrender.com/bookingapp/api/", "api_key": "b9d2f4c7a1e8d3f6c5a0b7e9d1c4f2a8"},
        {"name": "Homestay", "url": "https://homestay-1-4xmm.onrender.com/bookingapp/api/", "api_key": "c7e2a4d9f1b8c6a3d5e0f2b7a9c4d1e8"},
        {"name": "Veedu", "url": "https://veedu.onrender.com/bookingapp/api/", "api_key": "c1a7f9d4b6e3a8c2d5f0b1e7c9a4d2f6"},
    ]

    hotel_rooms = None
    combined_bookings = []

    # Fetch bookings from all websites
    for site in websites:
        headers = {"API-KEY": site["api_key"]}
        try:
            response = requests.get(site["url"], headers=headers, timeout=5)
            if response.status_code != 200:
                continue

            data = response.json()
            hotels = data if isinstance(data, list) else data.get("results", [])

            for hotel in hotels:
                if hotel.get("name", "").lower() == hotel_name.lower():
                    if hotel_rooms is None:
                        hotel_rooms = hotel.get("rooms", [])

                    bookings = hotel.get("bookings", [])
                    for booking in bookings:
                        booking["website"] = site["name"]
                        count = booking.get("count", 1)
                        for _ in range(count):
                            combined_bookings.append({
                                "name": booking.get("name"),
                                "email": booking.get("email"),
                                "room_type": booking.get("room_type"),
                                "check_in": booking.get("check_in"),
                                "check_out": booking.get("check_out"),
                                "total_amount": booking.get("total_amount"),
                                "website": site["name"]
                            })
        except requests.exceptions.RequestException:
            continue

    if not hotel_rooms:
        hotel_rooms = []

    
    for room in hotel_rooms:
        total_rooms = room.get("total_rooms", 0)
        room_booking_list = []
        website_stats = {}
        booked_numbers = set()

        for booking in combined_bookings:
            if booking["room_type"] == room["room_type"]:
                
                for num in range(1, total_rooms + 1):
                    if num not in booked_numbers:
                        booking["room_number"] = num
                        booked_numbers.add(num)
                        break

                room_booking_list.append(booking)

                site_name = booking["website"]
                if site_name not in website_stats:
                    website_stats[site_name] = []
                website_stats[site_name].append(booking["room_number"])

        room["booked_rooms"] = len(room_booking_list)
        room["available_rooms"] = total_rooms - len(room_booking_list)
        room["room_bookings"] = room_booking_list
        room["website_stats"] = website_stats

    return render(
        request,
        "hotel_result.html",
        {
            "hotel_name": hotel_name,
            "rooms": hotel_rooms
        }
    )