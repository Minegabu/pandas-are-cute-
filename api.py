import cgi
from flask import Flask,render_template,g,request,redirect,url_for,send_from_directory,flash
import requests
import json
import sqlite3
app = Flask(__name__)
form = cgi.FieldStorage()
searchterm =  form.getvalue('searchbox')
DATABASE = "Pandas-are-cute.db"
key = "4e67ce31-eac7-4daf-b7f7-390d7bf699b0"




def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db




def decimal_str(x: float, decimals: int = 10) -> str:
    return format(x, f".{decimals}f").lstrip().rstrip('0')

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
    if request.method == "POST":
        cursor = get_db().cursor()
        uuid = requests.get("https://api.mojang.com/users/profiles/minecraft/lilycraft132").json()
        profiles1 = requests.get("https://api.hypixel.net/player?key=9d49337e-bf1c-4825-84e4-71c529e778a3&uuid="+uuid["id"]).json()
        profliedata = list(profiles1["player"]["stats"]["SkyBlock"]["profiles"].keys())[0]
        data = requests.get("https://api.hypixel.net/skyblock/profile?key=9d49337e-bf1c-4825-84e4-71c529e778a3&profile="+profliedata).json()
        purse = data["profile"]["members"]["f95ceea60a084921a25b22bc726fafaa"]["coin_purse"]
        bank = data["profile"]["banking"]["balance"]
        sql = "INSERT INTO data (Purse,Bank) VALUES(?,?)"
        cursor.execute(sql,(purse,bank))
        print(request.form["ingamename"])
        get_db().commit()
        return render_template("contents.html")

if __name__ == "__main__":
    app.run(debug=True)