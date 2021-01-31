from django.http import HttpResponse
from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from .forms import *

import os, psycopg2

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

#DATABASE_URL = os.environ.get('DATABASE_URL')
#Uncomment to run locally
DATABASE_URL = "postgres://djwdentlsyoofv:200acd31c851de859734d5567f8742a9c71341d00650392ca2f6b1f6367543a2@ec2-54-237-155-151.compute-1.amazonaws.com:5432/d8mgcedgv549fr"

def addQuery( label, conn ) :
    myConnection = psycopg2.connect( host=hostname, user=username, password=password, dbname=database )
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
    myConnection.close()

def uploadPhoto( photo ) :
    im = cv2.imread(photo)
    bbox, label, conf = cv.detect_common_objects(im)
    output_image = draw_bbox(im, bbox, label, conf)
    addQuery( label )

def grocery_img_view(request):

    if request.method == 'POST':
        form = imageform(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return redirect('success')
    else:
        form = imageform()
    return render(request, 'hotel_image_form.html', {'form' : form})


def success(request):
    return HttpResponse('successfully uploaded')

def searchTitles(_title):
    print('HERE')
    con = None
    responseData = {}
    title = _title
    songs2 = []
    artist2 = []
    print(title)
    try:


        # create a new database connection by calling the connect() function
        con = psycopg2.connect(DATABASE_URL)

        #  create a new cursor
        cur = con.cursor()

        # execute an SQL statement to get the HerokuPostgres database version
        query = "SELECT name FROM release WHERE name ~* '.*{}.*'".format(title)
        cur.execute(query)

        rtnVals = []
        rtnVals = cur.fetchall()

        #Format the return object
        songs = [a_tuple[0] for a_tuple in rtnVals]

        query = "SELECT artists FROM release WHERE name ~* '.*{}.*'".format(title)
        cur.execute(query)

        rtnVals = []
        rtnVals = cur.fetchall()

        #Format the return object
        artist2 = [a_tuple[0] for a_tuple in rtnVals]


        responseData['data'] = songs
        songs2=songs

         # close the communication with the HerokuPostgres
        cur.close()
    except Exception as error:
        print('Cause: {}'.format(error))

    finally:
        # close the communication with the database server by calling the close()
        if con is not None:
            con.close()
            print('Databse connection closed.')

    #Returning a JSON object
    return songs2, artist2

def songDetails(_title):
    print('title: ' + str(_title) + '----------------------------------')
    #Input a song title and output all the details of it.
    #Called when the user clicks on a song title
    con = None
    responseData = {}
    title = _title
    data2=[]
    try:
        con = psycopg2.connect(DATABASE_URL)

        #  create a new cursor
        cur = con.cursor()

        # execute an SQL statement to get the HerokuPostgres database version
        #Query for the Id of the song selected
        queryId = "SELECT id FROM release WHERE name LIKE '%{}%'".format(title)
        cur.execute(queryId)

        rtnObj = cur.fetchone()
        if rtnObj == None:
            responseData["error"] = "No results return from title query: " + title
            return JsonResponse(responseData)

        objId = rtnObj[0]

        # Query for all details of the song selected
        queryDetails = "SELECT * FROM lyrics JOIN release ON release.id = lyrics.id JOIN sound ON sound.id = lyrics.id WHERE lyrics.id = '{}'".format(objId)
        cur.execute(queryDetails)
        rtnObj = cur.fetchall()
        #Check if an object was returned

        #Format song details
        songData = rtnObj[0]
        data2 = ["Title", str(songData[6]), "Artists", str(songData[4]), "Duration", str(songData[5]), "Popularity", str(songData[7]), "Release Date", str(songData[8]), "Year", str(songData[9]), "Speechiness", str(songData[1]), "Explicit", str(songData[2]), "Acousticness", str(songData[11]), "Danceability", str(songData[12]), "Energy", str(songData[13]), "Instrumentalness", str(songData[14]), "Key", str(songData[15]), "Loudness", str(songData[16]), "Mode", str(songData[17]), "Tempo", str(songData[18]), "Valence",  str(songData[19])]
        print(data2)
         # close the communication with the HerokuPostgres
        cur.close()
    except Exception as error:
        print('Cause, {}'.format(error))

    finally:
        # close the communication with the database server by calling the close()
        if con is not None:
            con.close()
            print('Databse connection closed.')

    #Return a JSON object

    return data2

# HELPER FUNCTION
def get_recommendations(title, cosine_sim, indices, metadata):
    # Get the index of the movie that matches the title
    idx = indices[title]
    #cosine_sim = cosine_similarity(temp.drop(['id'], axis=1), temp.drop(['id'], axis=1))
    # Get the pairwsie similarity scores of all movies with that movie
    sim_scores = list(enumerate(cosine_sim[idx]))

    # Sort the movies based on the similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the scores of the 10 most similar movies
    sim_scores = sim_scores[1:11]

    # Get the movie indices
    movie_indices = [i[0] for i in sim_scores]

    # Return the top 10 most similar movies
    print(movie_indices)
    print(metadata['name'].iloc[movie_indices[0]])
    songlist = []
    for x in range(0,9):
        songlist.append(str(metadata['name'].iloc[movie_indices[x]]))
    return songlist

#CALL THIS ONE.
def getSimilarSongs(_title):
    # Input Song Title
    # Output Song List of similar songs.
    responseData = {}
    df = pd.read_csv("data/data3000.csv")
    df = df.drop(['artists','id', 'release_date'], axis=1)

    cosine_sim = cosine_similarity(df.drop(['name'], axis=1), df.drop(['name'], axis=1))

    metadata = df.reset_index()
    indices = pd.Series(metadata.index, index=metadata['name'])

    title = _title
    simSongList = get_recommendations(title, cosine_sim, indices, metadata)
    return simSongList


def index(request):

    return render(request, 'index.html')

def aboutus(request):

    return render(request, 'aboutus.html')

def addpantry(request):

    return render(request, 'addpantry.html')

def mypantry(request):

    return render(request, 'mypantry.html')
