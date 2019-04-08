from flask import Flask, render_template, request,jsonify
from coach import Coach
import pymongo
from simplecrypt import encrypt, decrypt
import datetime
import pyvalidator
import phonenumbers
from matches import Matches
from webs import FrameTransfer

app = Flask(__name__,static_url_path='/static')
UPLOAD_FOLDER = './static/images'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
FrameTransfer()

@app.route('/form')
def form():
    return render_template('test.html')




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



@app.route('/deactivate_coach', methods=['POST'])
def deactivate_coach():
	coach = Coach()
	username = request.get_json()["username"]
	return coach.deactivate_coach(username)




@app.route('/activate_coach', methods=['POST'])
def activate_coach():
	coach = Coach()
	username = request.get_json()["username"]
	return coach.activate_coach(username)



@app.route('/update_coach_name', methods=['POST'])
def update_coach_name():
	coach = Coach()
	username = request.get_json()["username"]
	name = request.get_json()["name"]
	return coach.update_name(username,name)



@app.route('/update_coach_password', methods=['POST'])
def update_coach_password():
	coach = Coach()
	username = request.get_json()["username"]
	password = request.get_json()["password"]	
	if len(password)<8:
		return jsonify({"response":"short"})
	return coach.update_password(username,password)


@app.route('/update_coach_email', methods=['POST'])
def update_coach_email():
	coach = Coach()
	username = request.get_json()["username"]
	email = request.get_json()["email"]
	if not pyvalidator.email(email):
		return jsonify({"response":"invalid_email"})
	
	return coach.update_email(username,email)


@app.route('/update_coach_address', methods=['POST'])
def update_coach_address():
	coach = Coach()
	username = request.get_json()["username"]
	address = request.get_json()["address"]
	if len(address)<10:
		return jsonify({"response":"short_address"})
	return coach.update_address(username,address)



@app.route('/update_coach_city', methods=['POST'])
def update_coach_city():
	coach = Coach()
	username = request.get_json()["username"]
	city = request.get_json()["city"]
	return coach.update_city(username,city)



@app.route('/update_coach_country', methods=['POST'])
def update_coach_country():
	coach = Coach()
	username = request.get_json()["username"]
	country = request.get_json()["country"]
	return coach.update_country(username,country)



@app.route('/update_coach_phone', methods=['POST'])
def update_coach_phone():
	coach = Coach()
	username = request.get_json()["username"]
	phone = request.get_json()["phone"]
	try:
		phonenumbers.parse(phone,None)
	except phonenumbers.phonenumberutil.NumberParseException:
		return jsonify({"response":"invalid_phone_number"})
	
	return coach.update_phone(username,phone)



@app.route('/update_coach_birthday', methods=['POST'])
def update_coach_birthday():
	coach = Coach()
	username = request.get_json()["username"]
	birthday = request.get_json()["birthday"]
	try:
		datetime.datetime.strptime(birthday,'%Y-%m-%d')
	except ValueError:
		return jsonify({"response":"invalid_birth_date"})

	return coach.update_birthday(username,birthday)


@app.route('/update_coach_image', methods=['POST'])
def update_coach_image():
	coach = Coach()
	username = request.form["username"]
	if 'image' not in request.files:
		return jsonify({"response":"no_photo"})
	image = request.files["image"]

	return coach.update_image(username,image,app)



@app.route('/add_player', methods=['POST'])
def add_player():
	coach = Coach()
	name = request.get_json()["name"]
	coach_username = request.get_json()["coach_username"]
	return coach.register_player_for_coach(name,coach_username)


@app.route('/delete_player', methods=['POST'])
def delete_player():
	coach = Coach()
	name = request.get_json()["name"]
	return coach.delete_player_for_coach(name)



@app.route('/show_player', methods=['POST'])
def show_player():
	coach = Coach()
	coach_username = request.get_json()["coach_username"]
	return coach.show_players_for_coach(coach_username)


@app.route('/add_match', methods=['POST'])
def register_match_for_player():
	matches = Matches()
	player_username = request.get_json()["player_username"]
	return matches.register_match_for_player(player_username)


@app.route('/delete_match', methods=['POST'])
def delete_match_for_player():
	matches = Matches()
	object_id = request.get_json()["object_id"]
	return matches.delete_match_for_player(object_id)



@app.route('/show_matches', methods=['POST'])
def show_matches_for_player():
	matches = Matches()
	player_username = request.get_json()["player_username"]
	return matches.show_matches_for_player(player_username)


@app.route('/start_processing', methods=['POST'])
def processing():
	matches = Matches()
	object_id = request.form["object_id"]
	return matches.start_processing(object_id)


@app.route('/processing_results', methods=['POST'])
def processing_results():
	matches = Matches()
	object_id = request.form["object_id"]
	return matches.processing_results(object_id)



if __name__=="__main__":
	app.run(host='0.0.0.0',port=8989)