import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import redirect,render


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
                response = requests.get(site["url"], headers=headers)
                
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
    
# -------------------- HOTEL AUTHENTICATION AND HOTEL DETAILS --------------------



def login_view(request):
    if request.method == "POST":
        hotel_name = request.POST.get('hotel_name')
        if hotel_name:
            
            request.session['hotel_name'] = hotel_name
           
            return redirect('hotel_result')  
    return render(request, 'login.html')


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

    result = []

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

                    rooms = hotel.get("rooms", [])
                    bookings = hotel.get("bookings", [])

                    
                    for room in rooms:

                        room_booking_list = []
                        booked_count=0

                        for booking in bookings:
                            if booking["room_type"] == room["room_type"]:
                                room_booking_list.append(booking)
                                booked_count+=booking.get("count",0)

                        room["booked_rooms"] = booked_count
                        room["room_bookings"] = room_booking_list

                    result.append({
                        "website": site["name"],
                        "hotel_data": hotel,
                        "url": site["url"],
                        "api_key": site["api_key"]
                    })

        except requests.exceptions.RequestException:
            continue

    return render(
        request,
        "hotel_result.html",
        {
            "hotel_name": hotel_name,
            "websites_found": result
        }
    )