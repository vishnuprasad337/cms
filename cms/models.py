from django.db import models

class Website(models.Model):

    name = models.CharField(max_length=100)
    api_url = models.URLField()
    api_key = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name