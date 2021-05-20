import cgi
from flask import Flask,render_template,g,request,redirect,url_for,send_from_directory,flash
import requests
import json
import sqlite3
import math
millnames = ['',' K',' M',' B',' Trillion']
app = Flask(__name__)
form = cgi.FieldStorage()
searchterm =  form.getvalue('searchbox')
DATABASE = "Pandas-are-cute.db"
key = "e84267a6-e22c-4f9d-8e5d-7e162e6dc79b"

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def millify(n):
    n = float(n)
    millidx = max(0,min(len(millnames)-1,
                        int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))

    return '{:.0f}{}'.format(n / 10**(3 * millidx), millnames[millidx])

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/data',methods=["get","POST"])
def add():
    if request.method == "POST":
        ign = request.form.get("yess")
        try:
            uuid = requests.get("https://api.mojang.com/users/profiles/minecraft/"+ign).json()
            print(uuid["id"])
            cursor = get_db().cursor()
            try:
                profiles1 = requests.get("https://api.hypixel.net/player?key=" + key + "&uuid="+uuid["id"]).json()
                profliedata = list(profiles1["player"]["stats"]["SkyBlock"]["profiles"].keys())[0]
                data = requests.get("https://api.hypixel.net/skyblock/profile?key="+ key + "&profile="+profliedata).json()
                try:
                    try:
                        purse = millify(round(data["profile"]["members"][uuid["id"]]["coin_purse"]))
                        bank = millify(round(data["profile"]["banking"]["balance"]))
                        sql_3 = "DELETE FROM data WHERE UUID='" + uuid["id"] +"'"
                        sql_2 = "INSERT INTO data (Purse,Bank,UUID) VALUES(?,?,?)"
                        cursor.execute(sql_3)
                        cursor.execute(sql_2,(purse,bank,uuid["id"]))
                        get_db().commit()
                        sql = "SELECT * FROM data WHERE UUID='" + uuid["id"] + "'"
                        cursor.execute(sql)
                        results = cursor.fetchall()
                        return render_template("contents.html",results=results)   
                    except:
                        print("Please try again")
                        return redirect('/')
                        
                except:
                    print("That player has their api turned off")
                    return redirect('/')
            except:
                print("That player has no profiles")
                return redirect('/')              
        except:
            print("That username does not exist ")
            return redirect('/')




 


if __name__ == "__main__":
    app.run(debug=True)
