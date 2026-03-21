import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import redirect,render
from django.contrib import messages

from .models import Register,RoomType,Booking,Website
from django.http import JsonResponse
from datetime import datetime,timedelta
from django.utils import timezone
import json

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
def connect_website(request):
    if request.method == "POST":
        name = request.POST.get("name")
        url = request.POST.get("url")
        hotel_name = request.session.get("hotel_name")
        api_key = request.POST.get("api_key")

        if not hotel_name:
            messages.error(request, "Please login first.")
            return redirect("index")

        api_url = f"{url}/bookingapp/api/"

        Website.objects.create(
            name=name,
            api_url=api_url,
            api_key=api_key,
            status="pending"
        )

        payload = {
            "hotel_name": hotel_name,
            "url": url,
            "name": name,
            "api_key": api_key
        }

        try:
            requests.post(f"{url}/connect-request/", json=payload, timeout=5)
        except Exception as e:
            pass  # no need message now

        return redirect("connect_website")

    
   

    approved_sites = Website.objects.filter(status="approved").order_by("id")

    return render(request, "connect.html", {
        "approved_sites": approved_sites
    })

# -------------------- HOTEL AUTHENTICATION --------------------

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
def sync_websites():
    websites = Website.objects.all()

    for site in websites:
        try:
            response = requests.get(
                f"{site.api_url.replace('/bookingapp/api','')}/connection-status/",
                params={"name": site.name},
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()

                if data.get("status") == "approved":
                    site.status = "approved"
                    site.save()

        except Exception as e:
            print("Sync error:", e)
# -------------------- HOTEL RESULT --------------------


from datetime import date

def hotel_results_page(request):
    hotel_name = request.session.get("hotel_name")
    if not hotel_name:
        return redirect("dashboard")
    sync_websites()
    websites = [
        
        {"name": "Veedu", "url": "https://veedu.onrender.com/bookingapp/api/", "api_key": "c1a7f9d4b6e3a8c2d5f0b1e7c9a4d2f6"},
    ]
    website=[]
    for site in websites:
        if Website.objects.filter(name=site["name"], status="approved").exists():
            website.append(site)
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
    "name": b.guest_name,
    "email": b.guest_email,
    "room_type": rt_name,
    "check_in": b.check_in,
    "check_out": b.check_out,
    "total_amount": b.total_amount,
    "website": "CMS",
    "room_number": b.room_number,
    "status": b.status  
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

       
        lookup = {
    int(b["room_number"]): b
    for b in final_room_bookings
    if b.get("room_number") and b.get("status", "Active") == "Active"
}
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
    print(f"Processing {hotel_name}: Found {len(hotel_rooms)} types and {len(combined_bookings)} total bookings.")
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
    phone = request.POST.get("phone")
    payment_mode = request.POST.get("payment_mode")

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
        website="Direct",
        phone=phone,
        payment_mode=payment_mode,
        status="Active"   
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

     # ------------------ BOOKING DETAILS ------------------
def room_type(rt):
    if not rt:
        return "unknown"
    return rt.lower().replace("-", " ").strip()


def all_bookings(request):
    hotel_name = request.session.get("hotel_name")
    if not hotel_name:
        return redirect("index")

    websites = [
        {
            "name": "Veedu",
            "url": "https://veedu.onrender.com/bookingapp/api/",
            "api_key": "c1a7f9d4b6e3a8c2d5f0b1e7c9a4d2f6"
        },
    ]

    today = date.today()
    combined_bookings = []
    hotel_rooms = []

    cancelled_external = request.session.get("cancelled_external", [])

   
    for site in websites:
        try:
            res = requests.get(site["url"], headers={"API-KEY": site["api_key"]}, timeout=5)

            if res.status_code == 200:
                data = res.json()
                hotels = data if isinstance(data, list) else data.get("results", [])

                for hotel in hotels:
                    if hotel.get("name", "").lower() == hotel_name.lower():

                        if not hotel_rooms:
                            hotel_rooms = hotel.get("rooms", [])

                        for b in hotel.get("bookings", []):
                            count = b.get("count", 1)

                            for _ in range(count):

                               
                                booking_uuid = f"{b.get('email')}_{b.get('check_in')}_{b.get('room_type')}"

                                rt = room_type(b.get("room_type"))

                                status = "Inactive" if booking_uuid in cancelled_external else "Active"

                                combined_bookings.append({
                                    "booking_id": booking_uuid,
                                    "source": "external",
                                    "name": b.get("name"),
                                    "email": b.get("email"),
                                    "room_type": rt,
                                    "check_in": b.get("check_in"),
                                    "check_out": b.get("check_out"),
                                    "total_amount": float(b.get("total_amount", 0)),
                                    "payment_mode": b.get("payment_mode", "Online"),
                                    "website": site["name"],
                                    "room_number": None,
                                    "status": status
                                })
        except:
            continue

   
    cms_bookings = Booking.objects.filter(room_type__hotel_name=hotel_name)

    for b in cms_bookings:
        combined_bookings.append({
            "booking_id": b.id,
            "source": "cms",
            "name": b.guest_name,
            "email": b.guest_email,
            "room_type": room_type(b.room_type.room_type),
            "room_number": int(b.room_number),
            "check_in": b.check_in,
            "check_out": b.check_out,
            "total_amount": float(b.total_amount),
            "payment_mode": b.payment_mode,
            "status": b.status,
            "website": "CMS"
        })

   
    final_bookings = []

    for room in hotel_rooms:
        rt_name = room_type(room.get("room_type"))
        total_rooms = room.get("total_rooms", 0)
        price = float(room.get("price", 0))

        occupied = set()

       
        for b in combined_bookings:
            if b["room_type"] == rt_name and b.get("room_number") and b["status"] == "Active":
                occupied.add(int(b["room_number"]))

        for b in combined_bookings:
            if b["room_type"] != rt_name:
                continue

           
            if not b.get("room_number") and b["status"] == "Active":
                for i in range(1, total_rooms + 1):
                    if i not in occupied:
                        b["room_number"] = i
                        occupied.add(i)
                        break

           
            try:
                cout = b["check_out"]
                if isinstance(cout, str):
                    cout = datetime.strptime(cout, "%Y-%m-%d").date()

                overstay = today > cout
                extra_days = (today - cout).days if overstay else 0
                extra_payment = extra_days * price
            except:
                overstay = False
                extra_payment = 0

            b["overstay"] = overstay
            b["extra_payment"] = round(extra_payment, 2)

            final_bookings.append(b)

    return render(request, "booking.html", {
        "bookings": final_bookings
    })


def cancel_booking(request):
    if request.method != "POST":
        return JsonResponse({"status": "error", "message": "Invalid request"})

    data = json.loads(request.body)
    booking_id = data.get("id")
    source = data.get("source")

    hotel_name = request.session.get("hotel_name")

   
    if source == "cms":
        try:
            booking = Booking.objects.get(id=booking_id)
            booking.status = "Inactive"   
            booking.save()

            return JsonResponse({"status": "success"})
        except Booking.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Booking not found"})

    
    elif source == "external":
        cancelled = request.session.get("cancelled_external", [])

        if booking_id not in cancelled:
            cancelled.append(booking_id)

        request.session["cancelled_external"] = cancelled

        return JsonResponse({"status": "success"})

    return JsonResponse({"status": "error", "message": "Unknown source"})