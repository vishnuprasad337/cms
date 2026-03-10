from django.db import models

class Website(models.Model):

    name = models.CharField(max_length=100)
    api_url = models.URLField()
    api_key = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name
class Register(models.Model):

    hotel_name=models.CharField(max_length=100)
    owner_name=models.CharField(max_length=100)
    email=models.EmailField(unique=True)
    address=models.TextField(max_length=100)
    password=models.CharField(max_length=100)
    city = models.CharField(max_length=100)

    def __str__(self):
        return self.hotel_name 
