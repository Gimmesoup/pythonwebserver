#import statements
#region
import re
import sqlite3
from flask import Flask, render_template, redirect, url_for, request
from geopy.geocoders import Nominatim
import geopy.distance
import random
#endregion
app = Flask(__name__)

#Main Pages Routing
#region

#Index route; query database for random restaurants to feature
@app.route('/')
def index():
   conn = sqlite3.connect('database.sqlite')
   cur = conn.cursor()
   cur.execute("SELECT RESTID, RNAME FROM RESTAURANT")
   restaurants = cur.fetchall()


   randRestIDs = random.sample(range(1, len(restaurants)), 6)
   randRestaurants = {}

   for rID in randRestIDs:
      randRestaurants[restaurants[rID][0]] = restaurants[rID][1]

   return render_template('index.html', featuredRestaurants = randRestaurants)

#Render Restaurant Selection Page with Restaurants within a 
#certain distance from given form data
#
#Get form data, convert to geolocation to extract Lat/Lon from
#Get Lat/Lon data of restaurants from database
#Do comparisons, render template with qualifying restaurants
@app.route('/restSelect', methods = ['POST'])
def restSelect():
   address = request.form['address']

   geolocator = Nominatim(user_agent="geocoder")
   geolocation = geolocator.geocode(address)

   try:
      coord1 = (geolocation.latitude, geolocation.longitude)
   except:
      return redirect(url_for('nofood')) #No location found from address

   maxDistance = 50 #The 'Nearby' distance
   nearbyRestaurants = {}


   conn = sqlite3.connect('database.sqlite')
   cur = conn.cursor()
   cur.execute("SELECT RESTID, RNAME, LAT, LONG FROM RESTAURANT")
   restaurantTable = cur.fetchall()
   for row in restaurantTable:
      coord2 = (row[2], row[3])
      if geopy.distance.distance(coord1, coord2).km <= maxDistance:
         nearbyRestaurants[row[0]] = row[1]

   if not nearbyRestaurants: #No nearby restaurants found
      return redirect(url_for('nofood'))

   return render_template('restSelect.html', nearbyRestaurants = nearbyRestaurants)

#Render Food Ordering/Selection Page of chosen Restaurant
#
#Get form data, get food items from database based on form data
#Render template with food items
@app.route('/order', methods = ['POST'])
def order():
   rID = request.form['restID']
   
   rFoods = {}

   conn = sqlite3.connect('database.sqlite')
   cur = conn.cursor()
   cur.execute("SELECT FNAME, PRICE FROM FOOD WHERE FOOD.RESTID = ?", (rID, ))
   foodItems = cur.fetchall()
   for row in foodItems:
      rFoods[row[0]] = row[1]

   return render_template('order.html', rFoods = rFoods, rID = rID)

#Render Successful Order Page
#Update database with order information
#
#Get form data, loop through data to calculate totals
#and to select item data for items chosen by user
#Render template with accumulated data
@app.route('/success', methods = ['POST'])
def success():
   rID = request.form['restID']
   userName = request.form['userName']
   itemList = list(request.form.items())

   numItems = 0
   totalPrice = 0
   finalItemList = []

   for entry in itemList[2:]:
      itemName, itemPrice = entry[0].split("$")
      itemAmount = int(entry[1])
      itemsTotalPrice = float(itemPrice) * itemAmount

      numItems+=itemAmount
      totalPrice+=itemsTotalPrice

      itemsTotalPrice = round(itemsTotalPrice, 2)

      if(itemAmount > 0):
         finalItemList.append((itemName.strip(), ("$" + str(itemsTotalPrice)), (itemAmount)))

   totalPrice = round(totalPrice, 2)

   conn = sqlite3.connect('database.sqlite')
   cur = conn.cursor()
   cur.execute("INSERT INTO ORDERS (RESTID, NUMITEMS, TOTALPRICE, USERNAME) VALUES (?, ?, ?, ?)", (rID, numItems, totalPrice, userName))
   conn.commit()

   return render_template('success.html', userName = userName, finalItemList = finalItemList, numItems = numItems, totalPrice = totalPrice)

@app.route('/nofood')
def nofood():
   return render_template('nofood.html')
#endregion

#Footer Page Routing
#region
@app.route('/footer_aboutus')
def footer_aboutus():
   return render_template('footer_aboutus.html')
@app.route('/footer_giftcards')
def footer_giftcards():
   return render_template('footer_giftcards.html')
@app.route('/footer_careers')
def footer_careers():
   return render_template('footer_careers.html')
@app.route('/footer_investors')
def footer_investors():
   return render_template('footer_investors.html')
@app.route('/footer_faq')
def footer_faq():
   return render_template('footer_faq.html')
@app.route('/footer_contactus')
def footer_contactus():
   return render_template('footer_contactus.html')
@app.route('/footer_termsofservice')
def footer_termsofservice():
   return render_template('footer_termsofservice.html')
@app.route('/footer_privacypolicy')
def footer_privacypolicy():
   return render_template('footer_privacypolicy.html')
@app.route('/footer_donotsellmyinfo')
def footer_donotsellmyinfo():
   return render_template('footer_donotsellmyinfo.html')
#endregion

if __name__ == '__main__':
   app.run(debug = True)