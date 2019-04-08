from flask import Flask, render_template, request,jsonify
from coach import Coach
import pymongo
from simplecrypt import encrypt, decrypt
import datetime
import pyvalidator
from flask_mail import Mail,Message

app = Flask(__name__,static_url_path='/static')
UPLOAD_FOLDER = './static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'vikas.kph@gmail.com'
app.config['MAIL_PASSWORD'] = 'mypasswordisnotweak'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

@app.route("/mail", methods=['POST'])
def index():
	email = request.get_json()["email"]
	name = request.get_json()["name"]
	body = request.get_json()["body"]
	typ = request.get_json()["type"]
	if int(typ)==0:
		typ = "Contact Request"
	else:
		typ = "Bug Alert!"
	msg = Message(typ, sender = 'vikas.kph@gmail.com', recipients = ['vikas.kph@gmail.com'])
	msg.body = body
	msg.body += "\nName: "+name
	msg.body += "\nSender Mail: "+email
	mail.send(msg)
	return "Sent"


@app.route('/insert_coach', methods=['POST'])
def register_coach():
	coach = Coach()
	password = request.form["password"]
	email = request.form["email"]
	city = request.form["city"]
	name = request.form["name"]
	dom_hand = request.form["dom_hand"]
	club = request.form["club"]
	typ = request.form["type"]

	if 'image' not in request.files:
            return jsonify({"response":"no_photo"})

	image = request.files["image"]

	if len(password)<8:
		return jsonify({"response":"password_short"})
	if not pyvalidator.email(email):
		return jsonify({"response":"invalid_email"})
	
	return coach.register_coach(password,name,email,city,dom_hand,club,image,typ,app)
	




@app.route('/login_coach', methods=['POST'])
def login_coach():
	coach = Coach()
	email = request.get_json()["email"]
	password = request.get_json()["password"]
	
	if len(password)<8:
		return jsonify({"response":"short"})
	if not pyvalidator.email(email):
		return jsonify({"response":"invalid_email"})
	
	return coach.login_coach(email,password)




@app.route('/add_player', methods=['POST'])
def add_player():
	coach = Coach()
	coach_username = request.form["coach_mail"]
	name = request.form["name"]
	dom_hand = request.form["dom_hand"]
	if 'image' not in request.files:
		return jsonify({"response":"no_photo"})

	image = request.files["image"]
	return coach.register_player_for_coach(name,dom_hand,coach_username,image,app)



@app.route('/show_player', methods=['POST'])
def show_player():
	coach = Coach()
	coach_username = request.get_json()["coach_mail"]
	return coach.show_players(coach_username)

@app.after_request
def add_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    return response

if __name__=="__main__":
	app.run(host='0.0.0.0',port=8989)