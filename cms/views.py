import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import redirect,render
from django.contrib import messages
from .models import Register,RoomType,Booking
from django.http import JsonResponse
from datetime import datetime,timedelta
from django.utils import timezone
import json
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
    return render(request,'indexmain.html')


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

        return redirect("dashboard")

    return render(request, "index.html")


# --------------------  AUTHENTICATION CONNECTION VIEW --------------------




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

            return redirect("dashboard")

        except Register.DoesNotExist:

            messages.error(request, "Invalid hotel name or password")
            return redirect("index")

    return redirect("dashboard")





from datetime import date

def hotel_results_page(request):
    hotel_name = request.session.get("hotel_name")
    if not hotel_name:
        return redirect("dashboard")

    websites = [
        {"name": "Booking.com", "url": "https://project-demo-11.onrender.com/bookingapp/api/", "api_key": "9f8a7c6b5d4e3f2a1b0c"},
        {"name": "Bookmyhotel", "url": "https://bookmyhotel-5.onrender.com/bookingapp/api/", "api_key": "a7c4e9d2f6b1c8e3d5f0a9b7c6d4e2f1"},
        {"name": "Quickstayhub", "url": "https://quickstayhub-2.onrender.com/bookingapp/api/", "api_key": "b9d2f4c7a1e8d3f6c5a0b7e9d1c4f2a8"},
        {"name": "Homestay", "url": "https://homestay-1-4xmm.onrender.com/bookingapp/api/", "api_key": "c7e2a4d9f1b8c6a3d5e0f2b7a9c4d1e8"},
        {"name": "Veedu", "url": "https://veedu.onrender.com/bookingapp/api/", "api_key": "c1a7f9d4b6e3a8c2d5f0b1e7c9a4d2f6"},
    ]

    hotel_rooms = []
    combined_bookings = []

   
    for site in websites:
        headers = {"API-KEY": site["api_key"]}
        try:
            response = requests.get(site["url"], headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                hotels = data if isinstance(data, list) else data.get("results", [])
                for hotel in hotels:
                    if hotel.get("name", "").lower() == hotel_name.lower():
                        if not hotel_rooms:
                            hotel_rooms = hotel.get("rooms", [])
                        for b in hotel.get("bookings", []):
                            count = b.get("count", 1)
                            for _ in range(count):
                                combined_bookings.append({
                                    "name": b.get("name"), "email": b.get("email"),
                                    "room_type": b.get("room_type"), "check_in": b.get("check_in"),
                                    "check_out": b.get("check_out"), "total_amount": b.get("total_amount"),
                                    "website": site["name"]
                                })
        except:
            continue

    
    today = date.today()
    for room_data in hotel_rooms:
        rt_name = room_data.get("room_type")
        db_room, _ = RoomType.objects.update_or_create(
            hotel_name=hotel_name, room_type=rt_name,
            defaults={"price": room_data.get("price"), "total_rooms": room_data.get("total_rooms", 0)}
        )
        
        for b in db_room.bookings.all():
            combined_bookings.append({
                "name": b.guest_name, "email": b.guest_email, "room_type": rt_name,
                "check_in": b.check_in, "check_out": b.check_out, "total_amount": b.total_amount,
                "website": "CMS", "room_number": b.room_number
            })

    
    for room in hotel_rooms:
        total_rooms_count = room.get("total_rooms", 0)
        rt_name = room.get("room_type")
        
       
        occupied_numbers = set()
        for b in combined_bookings:
            if b["room_type"] == rt_name and b.get("room_number"):
                occupied_numbers.add(int(b["room_number"]))

        
        final_room_bookings = []
        website_stats = {}

        for b in combined_bookings:
            if b["room_type"] != rt_name: continue

            
            if not b.get("room_number"):
                for n in range(1, total_rooms_count + 1):
                    if n not in occupied_numbers:
                        b["room_number"] = n
                        occupied_numbers.add(n)
                        break
            
            
            b["overstay"] = False
            try:
                cout = b["check_out"]
                if isinstance(cout, str): cout = datetime.strptime(cout, "%Y-%m-%d").date()
                if today > cout:
                    b["overstay"] = True
                    b["extra_days"] = (today - cout).days
                    b["extra_payment"] = b["extra_days"] * room["price"]
            except: pass

            final_room_bookings.append(b)
            
            
            site = b["website"]
            if site not in website_stats: website_stats[site] = []
            website_stats[site].append(b["room_number"])

       
        lookup = {int(b["room_number"]): b for b in final_room_bookings if b.get("room_number")}
        ordered_grid = []
        for i in range(1, total_rooms_count + 1):
            if i in lookup:
                ordered_grid.append({"number": i, "is_occupied": True, "data": lookup[i]})
            else:
                ordered_grid.append({"number": i, "is_occupied": False, "data": None})

        room["ordered_grid"] = ordered_grid
        room["booked_rooms"] = len(final_room_bookings)
        room["available_rooms"] = total_rooms_count - len(final_room_bookings)
        room["website_stats"] = website_stats
        total_rooms=sum(room.get("total_rooms",0)for room in hotel_rooms)
        booked_rooms=sum(room.get("booked_rooms",0)for room in hotel_rooms)
        available_rooms=sum(room.get("available_rooms",0)for room in hotel_rooms)
        request.session["dashboard_rooms"] = {
            "total_rooms": total_rooms,
            "booked_rooms": booked_rooms,
            "available_rooms": available_rooms
        }

    return render(request, "hotel_result.html", {"hotel_name": hotel_name, "rooms": hotel_rooms})
# -------------------- CMS MANUAL BOOKING --------------------

def manual_booking(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request method"})

    hotel_name = request.session.get("hotel_name")
    room_type_name = request.POST.get("room_type")
    room_number=request.POST.get("room_number")
    guest_name = request.POST.get("guest_name")
    guest_email = request.POST.get("guest_email")
    check_in = request.POST.get("check_in")
    check_out = request.POST.get("check_out")

    try:
        room = RoomType.objects.get(room_type=room_type_name, hotel_name=hotel_name)

        booked_numbers = set(room.bookings.values_list("room_number", flat=True))
        
        if not room_number:
            return JsonResponse({"status": "error", "message": "No rooms available"})

        try:
            check_in_date = datetime.strptime(check_in, "%Y-%m-%d").date()
            check_out_date = datetime.strptime(check_out, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse({"status": "error", "message": "Invalid date format"})

        nights = (check_out_date - check_in_date).days
        if nights <= 0:
            return JsonResponse({"status": "error", "message": "Check-out must be after check-in"})

        total_amount = nights * room.price

        booking = Booking.objects.create(
            room_type=room,
            guest_name=guest_name,
            guest_email=guest_email,
            room_number=room_number,
            check_in=check_in_date,
            check_out=check_out_date,
            total_amount=total_amount,
            website="Direct"
        )

        return JsonResponse({
            "status": "success",
            "room_number": booking.room_number,
            "guest_name": booking.guest_name,
            "total_amount": booking.total_amount
        })

    except RoomType.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Room type not found"})


# -------------------- DASHBOARD --------------------
def dashboard(request):
    hotel_name = request.session.get("hotel_name")
    if not hotel_name:
        return redirect("index")

    room_types = RoomType.objects.filter(hotel_name=hotel_name)
    booking = Booking.objects.filter(room_type__hotel_name=hotel_name)
    dashboard_rooms=request.session.get("dashboard_rooms")
    if dashboard_rooms:
        total_rooms = dashboard_rooms.get("total_rooms", 0)
        booked_rooms = dashboard_rooms.get("booked_rooms", 0)
        available_rooms = dashboard_rooms.get("available_rooms", 0)
    else:
        total_rooms = sum(room.total_rooms for room in room_types)
        booked_rooms = booking.count()
        available_rooms = total_rooms - booked_rooms


    today = timezone.now().date()
    

    active_bookings = booking.filter(
        check_in__lte=today,
        check_out__gte=today
    ).count()

    total_revenue = sum(b.total_amount for b in booking)
    room_types_count = room_types.count()

    occupancy_rate = round((booked_rooms / total_rooms) * 100, 2) if total_rooms else 0
    booked_percentage = occupancy_rate
    available_percentage = 100 - occupancy_rate
    today = timezone.now().date()

    booking = Booking.objects.filter(room_type__hotel_name=hotel_name)

    today_checkins = booking.filter(check_in=today).count()
    today_checkouts = booking.filter(check_out=today).count()

    today_revenue = sum(b.total_amount for b in booking.filter(check_in=today))
    today_occupancy = occupancy_rate

    overstay_count = booking.filter(check_out__lt=today, check_in__lte=today).count()
    chart_labels = []
    chart_data = []

    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        chart_labels.append(day.strftime("%a"))
        count = booking.filter(check_in=day).count()
        chart_data.append(count)

    context = {
        "hotel_name": hotel_name,
        "total_rooms": total_rooms,
        "available_rooms": available_rooms,
        "booked_rooms": booked_rooms,
        "room_types_count": room_types_count,
        "active_bookings": active_bookings,
        "total_revenue": total_revenue,
        "occupancy_rate": occupancy_rate,
        "booked_percentage": booked_percentage,
        "available_percentage": available_percentage,
        "today_checkins": today_checkins,
        "today_checkouts": today_checkouts,
        "today_revenue": today_revenue,
        "today_occupancy": today_occupancy,
        "overstay_count": overstay_count,
        "chart_labels": json.dumps(chart_labels),
        "chart_data": json.dumps(chart_data),
        "current_date": timezone.now(),
    }

    return render(request, "index.html", context)
