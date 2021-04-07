import cgi
from flask import Flask,render_template,g,request,redirect,url_for,send_from_directory,flash
import requests
import json
import sqlite3
app = Flask(__name__)
form = cgi.FieldStorage()
searchterm =  form.getvalue('searchbox')

def getting_stats():
    while 1:
        try:
            uuid = requests.get("https://api.mojang.com/users/profiles/minecraft/" +ingamename).json()
            print(uuid['id'])
            data = requests.get("https://api.hypixel.net/player?key=5dc79cc8-f597-4eb8-b8a9-f22cf281c2eeuuid="+uuid["id"]).json()
            skywarsWins = data["player"]["stats"]["SkyWars"]["wins"]
            bedwarsWins = data["player"]["stats"]["Bedwars"]["wins_bedwars"]
            print("You have this many skywars wins:" + str(skywarsWins))
            print("You have this many bedwars wins:" + str(bedwarsWins))
        except:
            print("Did you put the wrong username?")

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/ingamename',methods=["get","POST"])
def data():
    print(request.form["ingamename"])
    print ("Gabriel's Gay")
    return render_template("contents.html")

if __name__ == "__main__":
    app.run(debug=True)