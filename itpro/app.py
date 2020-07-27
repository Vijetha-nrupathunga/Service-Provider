from haversine import haversine
from geopy.geocoders import Nominatim
from flask import Flask
from flask import render_template
from flask import redirect
from flask import url_for
from flask import request
#from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL
from flask import session
from flask import flash
import yaml
import os
#from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

#Bootstrap(app)


db = yaml.load(open('itpro\\db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

app.config['SECRET_KEY'] = os.urandom(20)
# Add the route to the Index page of the App
loginnn={}
@app.route('/')
def index():
    cur =  mysql.connection.cursor()
    alldata=[]
    result1 = cur.execute("SELECT * FROM users")
    alldata.append(result1)
    result2 = cur.execute("SELECT * FROM plumber")
    alldata.append(result2)
    result3 = cur.execute("SELECT * FROM electrician")
    alldata.append(result3)
    result4 = cur.execute("SELECT * FROM carpenter")
    alldata.append(result4)
    if (len(alldata) > 0):
        return render_template('index.html', data=alldata)
@app.route('/contact')
def contact():
    return render_template('contact.html')
# route to add New User
@app.route('/newuser/', methods = ['GET', 'POST'])
def newuser():
    error = None
    if request.method == 'POST':
        form = request.form
        name =  form['name']
        address = form['address']
        contact = form['contact']
        email = form["email"]
        password = form["password"]
        geolocator = Nominatim(user_agent="service")
        loc = geolocator.geocode(address)
        if(loc != None):
            latitude = loc.latitude  
            longitude = loc.longitude 
            loginnn["latitude"]=latitude
            loginnn["longitude"]=longitude   
            cur =  mysql.connection.cursor()
            cur.execute("INSERT INTO users(name, address, contact, email, password, latitude, longitude) VALUES(%s, %s, %s, %s, %s, %s, %s)",(name, address, contact, email, password, latitude, longitude))
            mysql.connection.commit()
            flash('signned up')
            return redirect('/service')
        else: error = 'unknown place.please try again '
    return render_template('newuser.html',error=error)

# Display All users from database
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    cur =  mysql.connection.cursor()
    result_value=cur.execute("select * from users")
    if request.method == 'POST':
        for r in cur.fetchall():
            if request.form['name']==r['name'] and request.form['password']==r['password']:
                loginnn["latitude"]=r['latitude']
                loginnn["longitude"]=r['longitude'] 
                return redirect('/service')
            elif request.form['name'] !=r['name'] or request.form['password'] !=r['password']:
                error = 'username doesnot match with the password'
    return render_template('index1.html',error=error)



@app.route('/service',methods=['GET','POST'])
def service():
    cur = mysql.connection.cursor()
    return render_template('service.html')

@app.route('/plumber/')
def plumber():
    cur=mysql.connection.cursor()
    res2 = cur.execute("SELECT id,latitude,longitude,distance FROM plumber")
    data2 = cur.fetchall()
    if (res2 > 0):
        i=1
        print(loginnn["latitude"])
        for dat in data2:
            for k,v in dat.items():
                h=haversine((loginnn["latitude"],loginnn["longitude"]),(dat["latitude"],dat["longitude"]))
                cur.execute("UPDATE plumber SET distance=%s where id=%s",(h,i) )
                mysql.connection.commit()
            i=i+1
        dist = cur.execute("SELECT * FROM plumber ORDER BY distance asc")
        data9 = cur.fetchall()
        msg="plumbers"
        let="P"
        return render_template('electrician.html',data=data9,msg=msg,let=let)

@app.route('/electrician/')
def electrician():
    cur=mysql.connection.cursor()
    res2 = cur.execute("SELECT id,latitude,longitude,distance FROM electrician")
    data2 = cur.fetchall()
    if (res2 > 0):
        i=1
        for dat in data2:
            for k,v in dat.items():
                h=haversine((loginnn["latitude"],loginnn["longitude"]),(dat["latitude"],dat["longitude"]))
                cur.execute("UPDATE electrician SET distance=%s where id=%s",(h,i) )
                mysql.connection.commit()
            i=i+1
        dist = cur.execute("SELECT * FROM electrician ORDER BY distance asc")
        data9 = cur.fetchall()
        msg="electricians"
        let="E"
    return render_template('electrician.html',data=data9,msg=msg,let=let)

@app.route('/carpenter/')
def carpenter():
    cur=mysql.connection.cursor()
    res2 = cur.execute("SELECT id,latitude,longitude,distance FROM carpenter")
    data2 = cur.fetchall()
    if (res2 > 0):
        i=1
        print(loginnn["latitude"])
        for dat in data2:
            for k,v in dat.items():
                h=haversine((loginnn["latitude"],loginnn["longitude"]),(dat["latitude"],dat["longitude"]))
                cur.execute("UPDATE carpenter SET distance=%s where id=%s",(h,i) )
                mysql.connection.commit()
            i=i+1
        dist = cur.execute("SELECT * FROM carpenter ORDER BY distance asc")
        data9 = cur.fetchall()
        msg="carpenters"
        let="C"
    return render_template('electrician.html',data=data9,msg=msg,let=let)

# Run the main App

if __name__ == '__main__':
    app.run(debug=True)
