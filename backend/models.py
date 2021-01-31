from django.db import models
from django.contrib.auth.models import User

class imagemodel(models.Model):
    grocery_img = models.ImageField(upload_to='images/')
