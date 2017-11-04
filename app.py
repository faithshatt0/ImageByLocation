import os
from flask import Flask, render_template, request
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map, icons
import requests
import json
import urllib2

app = Flask(__name__, template_folder = "templates")

# you can set key as config
app.config['GOOGLEMAPS_KEY'] = "###"

# you can also pass key here
GoogleMaps(app, key="###")


@app.route('/')
def index():
    return render_template('index.html')


@app.route("/", methods = ['POST', 'GET'])
def main():
    
    # c.c.j.c
    if request.method == 'POST':
        if request.form['text'] == '':
            return render_template('index.html')
        else:
            location_place = request.form['text']

    url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {'sensor': 'false', 'address': location_place}
    
    r = requests.get(url, params=params)
    results = r.json()['results']
    
    if len(results) <= 0:
        invalid = '''<script> invalid_city(); </script>'''
        return render_template("index.html", invalid = invalid)
        
    location = results[0]['geometry']['location']
    if type(location) is not dict:
        return render_template('index.html')
        
    api_key = "###"
    api_secret = "###"
    popular_image = ""
        
    latitude = location['lat']
    longitude = location['lng']
    
        
    #generates list of photos based on location (lat,lon)
    url = "https://api.flickr.com/services/rest/?method=flickr.photos.search&api_key=" + str(api_key) + "&lat=" + str(latitude) + "&lon=" + str(longitude) + "&sort=interestingness-desc&extras=views&per_page=250&format=json&nojsoncallback=1"
    response = urllib2.urlopen(url)
    data = json.load(response)
        
    
    for i in range(250):
               #goes through each photo in list of photos from location ^^^
           photoID = data["photos"]["photo"][i]["id"]
               
               #finds the most popular image from list, based on views
           if(i == 0):
                  first_photo_views = int(data["photos"]["photo"][i]["views"])
               
    current_photo_views = int(data["photos"]["photo"][i]["views"])
               
    if(current_photo_views > first_photo_views):
        popular_image = data["photos"]["photo"][i]["id"]
                  
        first_photo_views = current_photo_views
        
    url = "https://api.flickr.com/services/rest/?method=flickr.photos.getSizes&api_key=" + api_key + "&photo_id=" + popular_image + "&format=json&nojsoncallback=1"
    response = urllib2.urlopen(url)
    data2 = json.load(response)
    if 'sizes' not in data2:
        invalid = '''<script> invalid_city(); </script>'''
        return render_template("index.html", invalid = invalid)
    
    image = str(data2['sizes']['size'][5]['source'])
    
    mymap = Map(
        identifier="resultsmap",
        style=(
            "height:100%;"
            "width:100%;"
            "top:0;"
            "left:0;"
            "position:absolute;"
            "z-index:200;"
        ),
        lat=latitude,
        lng=longitude,
        
        markers=[
            {
                'icon': 'http://maps.google.com/mapfiles/ms/icons/red-dot.png',
                'lat':  latitude,
                'lng':  longitude,
                'infobox': '<img src=" '+ image +' " />'
            }
        ]
    )
    return render_template('results.html', mymap=mymap, )

if __name__ == '__main__':
    app.run(debug = True,
    port = int(os.getenv('PORT',8080)),
    host = os.getenv('IP','0.0.0.0')
    )
