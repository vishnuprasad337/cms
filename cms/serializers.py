from rest_framework import serializers
from .models import Register,Website

class WebsiteSerializers(serializers.ModelSerializer):
    class Meta:
        model=Website
        fields="__all__"


class RegisterSerializers(serializers.ModelSerializer):
    class Meta:
        model=Register
        fields="__all__"