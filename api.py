''' get players stats on skyblock'''
''' code'''

from tabulate import tabulate
import cgi
from flask import Flask,render_template,g,request,redirect,url_for,send_from_directory,flash
import requests
import json
import sqlite3
import math
#for making it easy to read
millnames = ['',' K',' M',' B',' T']
app = Flask(__name__)
form = cgi.FieldStorage()
searchterm =  form.getvalue('searchbox')
#database
DATABASE = "Pandas-are-cute.db"
#api key
key = "e84267a6-e22c-4f9d-8e5d-7e162e6dc79b"
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
#connect the database
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db
 
#turn the numbers into readable numbers that people can understand
def millify(n):
    n = float(n)
    millidx = max(0,min(len(millnames)-1,
                        int(math.floor(0 if n == 0 else math.log10(abs(n))/3))))
    return '{:.0f}{}'.format(n / 10**(3 * millidx), millnames[millidx])

#the homepage function
@app.route('/')
def home():
    return render_template("home.html")

#function to get the skill xp and turn it into level and percent to next level
def compute(skillxp):
    try:
        #get the skill data 
        skills = requests.get("https://api.hypixel.net/resources/skyblock/skills").json()
        #turn it into the right list of dictonarys
        levels = skills["collections"]["FARMING"]["levels"]
        #sort through the list of dictonarys
        sorted = [item for item in levels if item["totalExpRequired"] < skillxp] 
        #get the level
        max = sorted[-1]["level"]
        #get the exp to next level
        exptonextlevel = sorted[-1]['totalExpRequired']-sorted[max-2]["totalExpRequired"]
        #get the amount of exp already to next level
        exptotalnextlevel = skillxp-sorted[max-1]["totalExpRequired"]
        #percent to next level
        nextlevel = exptotalnextlevel/exptonextlevel
        #if you are over the level cap 
        if nextlevel > 1:
            nextlevel = 0
        return(round(nextlevel+max,2))
    except:
        #if you are over 50 on a skill that caps out at 50
        sorted = [item for item in levels if item["totalExpRequired"] > skillxp] 
        max = sorted[-1]["level"]
        return(max)



@app.route('/pursedata',methods=["get","POST"])
def add():
    if request.method == "POST":
        global ign
        ign = request.form.get("yess")
        global uuid
        uuid = requests.get("https://api.mojang.com/users/profiles/minecraft/"+ign).json()
        print(uuid["id"])
        global uuidglobal
        uuidglobal = uuid["id"]
        cursor = get_db().cursor()
        profiles1 = requests.get("https://api.hypixel.net/player?key=" + key + "&uuid="+uuid["id"]).json()
        profliedata = list(profiles1["player"]["stats"]["SkyBlock"]["profiles"].keys())[0]
        global cutename
        cutename = profiles1["player"]["stats"]["SkyBlock"]["profiles"][profliedata]["cute_name"]
        data = requests.get("https://api.hypixel.net/skyblock/profile?key="+ key + "&profile="+profliedata).json()
        profiles2 = requests.get("https://api.hypixel.net/skyblock/profiles?key="+key+"&uuid="+uuid["id"]).json()
        skindata = requests.get("https://sessionserver.mojang.com/session/minecraft/profile/"+uuid["id"]).json()
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

        if alchemylevel > 50:
            alchemylevel = 50
        if taminglevel > 50:
           taminglevel = 50
        if foraginglevel > 50:
            foraginglevel = 50
        #sql_3 = "DELETE FROM data WHERE UUID='" + uuid["id"] +"'"
        #sql_2 = "INSERT INTO data (purse,bank,UUID,farming,taming,mining,enchanting,combat,fishing,foraging,alchemy) VALUES(?,?,?,?,?,?,?,?,?,?,?)"
        sql4 = """UPDATE data SET purse=? WHERE uuid=?"""
        print(sql4)
        print(purse)
        print(uuid["id"])
        cursor.execute(sql4,(purse,uuid["id"]))
        #updating purse data for user 
        cursor.execute("""UPDATE data SET bank=? WHERE uuid=?""",(bank,uuid["id"]))
        cursor.execute("""UPDATE data SET farming=? WHERE uuid=?""",(farminglevel,uuid["id"]))
        cursor.execute("""UPDATE data SET taming=? WHERE uuid=?""",(taminglevel,uuid["id"]))
        cursor.execute("""UPDATE data SET mining=? WHERE uuid=?""",(mininglevel,uuid["id"]))
        cursor.execute("""UPDATE data SET enchanting=? WHERE uuid=?""",(enchantinglevel,uuid["id"]))
        cursor.execute("""UPDATE data SET combat=? WHERE uuid=?""",(combatlevel,uuid["id"]))
        cursor.execute("""UPDATE data SET fishing=? WHERE uuid=?""",(fishinglevel,uuid["id"]))
        cursor.execute("""UPDATE data SET foraging=? WHERE uuid=?""",(foraginglevel,uuid["id"]))
        cursor.execute("""UPDATE data SET alchemy=? WHERE uuid=?""",(alchemylevel,uuid["id"]))
        get_db().commit()
        sql = "SELECT * FROM data WHERE UUID='" + uuid["id"] +"'"
        cursor.execute(sql)    
        results = cursor.fetchall()
        return render_template("contents.html",results=results, name=ign,profile=cutename)     
    else:
        uuid = requests.get("https://api.mojang.com/users/profiles/minecraft/"+ign).json()
        cursor = get_db().cursor()
        sql = "SELECT * FROM data WHERE UUID ='" + uuid["id"] +"'"
        cursor.execute(sql)
        results = cursor.fetchall()
        return render_template("contents.html",results=results,name=ign,profile=cutename)

@app.route('/skilldata',methods=["get","POST"])
def skill():
    cursor = get_db().cursor()
    sql = "SELECT * FROM data WHERE UUID='" + uuidglobal + "'"
    print(uuidglobal)
    cursor.execute(sql)
    results = cursor.fetchall()
    return render_template("contents1.html",name=ign,profile=cutename,results=results,)
         

@app.route('/friends',methods=["get","POST"])
def friend():
    ign = request.form.get("IGN")
    return render_template("friends.html",)

if __name__ == "__main__":
    app.run(debug=True)

''' end of code'''