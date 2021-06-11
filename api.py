''' get players stats on skyblock'''

''' code'''
from tabulate import tabulate
import cgi
from flask import Flask,render_template,g,request,redirect,url_for,send_from_directory,flash
import requests
import json
import sqlite3
import math
millnames = ['',' K',' M',' B',' T']
app = Flask(__name__)
form = cgi.FieldStorage()
searchterm =  form.getvalue('searchbox')
DATABASE = "Pandas-are-cute.db"
key = "e84267a6-e22c-4f9d-8e5d-7e162e6dc79b"
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
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

def compute(skillxp):
    cursor = get_db().cursor()
    skills = requests.get("https://api.hypixel.net/resources/skyblock/skills").json()
    levels = skills["collections"]["FARMING"]["levels"]
    sorted = [item for item in levels if item["totalExpRequired"] < skillxp] 
    level = sorted[-1]["level"]
    return(level)



@app.route('/pursedata',methods=["get","POST"])
def add():
   if request.method == "POST":
        global ign
        ign = request.form.get("yess")
        try:
            global uuid
            uuid = requests.get("https://api.mojang.com/users/profiles/minecraft/"+ign).json()
            print(uuid["id"])
            cursor = get_db().cursor()
            try:
                profiles1 = requests.get("https://api.hypixel.net/player?key=" + key + "&uuid="+uuid["id"]).json()
                profliedata = list(profiles1["player"]["stats"]["SkyBlock"]["profiles"].keys())[0]
                global cutename
                cutename = profiles1["player"]["stats"]["SkyBlock"]["profiles"][profliedata]["cute_name"]
                data = requests.get("https://api.hypixel.net/skyblock/profile?key="+ key + "&profile="+profliedata).json()
                profiles2 = requests.get("https://api.hypixel.net/skyblock/profiles?key="+key+"&uuid="+uuid["id"]).json()
                try:
                    purse = millify(round(data["profile"]["members"][uuid["id"]]["coin_purse"]))
                    bank = millify(round(data["profile"]["banking"]["balance"]))
                    farmingtotal =  profiles2["profiles"][2]["members"][uuid["id"]]["experience_skill_farming"]
                    miningtotal = profiles2["profiles"][2]["members"][uuid["id"]]["experience_skill_mining"]
                    enchantingtotal = profiles2["profiles"][2]["members"][uuid["id"]]["experience_skill_enchanting"]
                    alchemytotal = profiles2["profiles"][2]["members"][uuid["id"]]["experience_skill_alchemy"]
                    combattotal = profiles2["profiles"][2]["members"][uuid["id"]]["experience_skill_combat"]
                    tamingtotal = profiles2["profiles"][2]["members"][uuid["id"]]["experience_skill_taming"]
                    fishingtotal = profiles2["profiles"][2]["members"][uuid["id"]]["experience_skill_fishing"]
                    foragingtotal = profiles2["profiles"][2]["members"][uuid["id"]]["experience_skill_foraging"]

                    mininglevel = compute(miningtotal)
                    enchantinglevel = compute(enchantingtotal)
                    alchemylevel = compute(alchemytotal)
                    combatlevel = compute(combattotal)
                    taminglevel = compute(tamingtotal)
                    fishinglevel = compute(fishingtotal)
                    foraginglevel = compute(foragingtotal)
                    farminglevel = compute(farmingtotal)
                    try:
                        sql_3 = "DELETE FROM data WHERE UUID='" + uuid["id"] +"'"
                        sql_2 = "INSERT INTO data (purse,bank,UUID,farming,taming,mining,enchanting,combat,fishing,foraging) VALUES(?,?,?,?,?,?,?,?,?,?)"
                        cursor.execute(sql_3)
                        cursor.execute(sql_2,(purse,bank,uuid["id"],farminglevel,taminglevel,mininglevel,enchantinglevel,combatlevel,fishinglevel,foraginglevel))
                        get_db().commit()
                        sql = "SELECT * FROM data WHERE UUID='" + uuid["id"] +"'"
                        cursor.execute(sql)    
                        results = cursor.fetchall()
                        return render_template("contents.html",results=results, name=ign,profile=cutename,)   
                    except:
                        flash("Please try again")
                        return redirect('/')       
                except:
                    flash(ign+ " has their api turned off")
                    return redirect('/')
            except:
                flash(ign+" has no profiles")
                return redirect('/')              
        except:
            flash("That username does not exist ")
            return redirect('/')

@app.route('/skilldata',methods=["get","POST"])
def skill():
    if request.method == "POST":
        cursor = get_db().cursor()
        sql = "SELECT * FROM data WHERE UUID+'" + uuid["id"] + "'"
        cursor.execute(sql)
        results = cursor.fetchall()
        return render_template("contents1.html",name=ign,profile=cutename,results=results)


@app.route('/friends',methods=["get","POST"])
def friend():
    if request.method == "POST":
        ign = request.form.get("yes")
        return render_template("friends.html")
 


if __name__ == "__main__":
    app.run(debug=True)

''' end of code'''