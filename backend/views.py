from __future__ import print_function
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from os import listdir
from os.path import isfile, join
from .forms import *
from PIL import Image
import PIL

import cv2
import matplotlib.pyplot as plt
import cvlib as cv
import os, psycopg2
from cvlib.object_detection import draw_bbox

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

#DATABASE_URL = os.environ.get('DATABASE_URL')
#Uncomment to run locally
DATABASE_URL = "postgres://djwdentlsyoofv:200acd31c851de859734d5567f8742a9c71341d00650392ca2f6b1f6367543a2@ec2-54-237-155-151.compute-1.amazonaws.com:5432/d8mgcedgv549fr"

hostname = 'localhost'
username = 'phillip'
password = 'Redwater1.'
database = 'tamuhack2021'

def addQuery( label ) :
    conn = psycopg2.connect( host=hostname, user=username, password=password, dbname=database )
    cur = conn.cursor()
    cur.execute ("SELECT COUNT(*) FROM groceries WHERE quantity > 1;")
    match = 0
    for name in cur.fetchall() :
        if name[0] == 0 :
            cur.execute("INSERT INTO groceries (name, quantity) VALUES ('" + label[0] + "', '1');")
            conn.commit()
            for i in range(len(label)-1) :
                cur.execute ("SELECT name FROM groceries")
                for name in cur.fetchall() :
                    if label[i+1] == name[0] :
                        print("You already have" + label[i+1] + "at home")
                        cur.execute("UPDATE groceries SET quantity = quantity + 1 WHERE name = '" + label[i+1] + "';")
                        conn.commit()
                        match = 1
                        break
                if match == 0 :
                    cur.execute("INSERT INTO groceries (name, quantity) VALUES ('" + label[i+1] + "', '1');")
                    conn.commit()
                match = 0
        else :
            for i in range(len(label)) :
                cur.execute ("SELECT name FROM groceries")
                for name in cur.fetchall() :
                    if label[i] == name[0] :
                        print("You already have" + label[i] + "at home")
                        cur.execute("UPDATE groceries SET quantity = quantity + 1 WHERE name = '" + label[i] + "';")
                        conn.commit()
                        match = 1
                        break
                if match == 0 :
                    cur.execute("INSERT INTO groceries (name, quantity) VALUES ('" + label[i] + "', '1');")
                    conn.commit()
                match = 0
    conn.close()

def uploadPhoto( photo ) :
    im = cv2.imread(photo)
    bbox, label, conf = cv.detect_common_objects(im)
    output_image = draw_bbox(im, bbox, label, conf)
    print(label)
    addQuery( label )
    return output_image

def grocery_img_view(request):
    print("we got here")
    if request.method == 'POST':
        form = imageform(request.POST, request.FILES)
        #print(form.__dict__)
        #print(form["grocery_img"])
        print(request.FILES["grocery_img"].name)
        if form.is_valid():
            file = request.FILES['grocery_img']

            img = Image.open(file)
            img.save(f'media/images/{request.FILES["grocery_img"].name}')
            photo = uploadPhoto(f'media/images/{request.FILES["grocery_img"].name}')
            cv2.imwrite(f'media/newimages/{request.FILES["grocery_img"].name}', photo)
    else:
        form = imageform()
    if "grocery_img" in request.FILES :
        return render(request, 'addpantry.html', {'url' : f'media/newimages/{request.FILES["grocery_img"].name}', 'form' : form})
    return render(request, 'addpantry.html', {'form' : form})

def success(request):
    return HttpResponse('successfully uploaded')

def index(request):

    return render(request, 'index.html')

def aboutus(request):

    return render(request, 'aboutus.html')

def addpantry(request):

    return render(request, 'addpantry.html')

def mypantry(request):
    mypath = 'media/newimages/'
    return render(request, 'mypantry.html', {'images' : [join(mypath, f) for f in listdir(mypath) if isfile(join(mypath, f))]})
