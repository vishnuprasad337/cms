from django.db import models


class Website(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("declined", "Declined"),
    ]

    name = models.CharField(max_length=100)
    api_url = models.URLField()

    api_key = models.CharField(max_length=200, blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

   
    def __str__(self):
        return self.name

class Register(models.Model):
    hotel_name = models.CharField(max_length=100)
    owner_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    address = models.TextField(max_length=100)
    password = models.CharField(max_length=100)
    city = models.CharField(max_length=100)

    def __str__(self):
        return self.hotel_name


class RoomType(models.Model):
    hotel_name = models.CharField(max_length=100)
    room_type = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_rooms = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.hotel_name} - {self.room_type}"

class Booking(models.Model):

    BOOKING_STATUS = [
        ("Active", "Active"),          
        ("CheckedOut", "Checked Out"), 
        ("Cancelled", "Cancelled"),    
    ]

    phone = models.CharField(max_length=15, null=True, blank=True)
    payment_mode = models.CharField(max_length=20, null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=BOOKING_STATUS,
        default="Active"
    )

    
    room_type = models.ForeignKey("RoomType", on_delete=models.CASCADE, related_name="bookings")
    guest_name = models.CharField(max_length=100)
    guest_email = models.EmailField()
    room_number = models.IntegerField()
    check_in = models.DateField()
    check_out = models.DateField()
    total_amount = models.FloatField()
    website = models.CharField(max_length=50, default="Direct")
    id_proof_photo = models.ImageField(   upload_to="id_proofs/",   null=True,   blank=True
     )
       

      

    def __str__(self):
        return f"{self.guest_name}"
