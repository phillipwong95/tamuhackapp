from django.db import models
from django.contrib.auth.models import User

class imagemodel(models.Model):
    name = models.CharField(max_length=255)
    grocery_img = models.ImageField(upload_to='images/')
