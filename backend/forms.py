from django import forms
from .models import *

class imageform(forms.ModelForm):

    class Meta:
        model = imagemodel
        fields = ['grocery_img'] 
