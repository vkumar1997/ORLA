from flask import jsonify
import pymongo
from passlib.hash import pbkdf2_sha256
from werkzeug import secure_filename
import os
import datetime
from bson.json_util import dumps
import glob

class Coach:
	def __init__(self):
		myclient = pymongo.MongoClient("mongodb://localhost:27017/")
		mydb = myclient["orla"]
		self.mongo = mydb["coaches"]
		self.players = mydb["players"]
		self.mongo.create_index("email",unique=True)
		

	def register_coach(self,password,name,email,city,dom_hand,club,image,typ,app):
		try:
			phash = pbkdf2_sha256.hash(password)
			dic = { "email_id": email, "coach_password": phash,"city":city,"coach_name": name, "type":typ, "dom_hand":dom_hand, "club":club, "status": 1,"timestamp":datetime.datetime.now()}
			x = self.mongo.insert_one(dic)
			extension = secure_filename(image.filename).split('.')[-1]
			username = str(x.inserted_id)
			image.save(os.path.join(app.config['UPLOAD_FOLDER'],username+'.' +extension))
			return jsonify({"response":"ok"})

		except pymongo.errors.DuplicateKeyError:
			return jsonify({"response":"duplicate"})
		except Exception as e:
			print(e)
			return jsonify({"response":"internal_server_error"})




	def login_coach(self,email,password):
		try:
			result = self.mongo.find_one({"email_id":email})
			phash = result["coach_password"]
			name = result["coach_name"]
			city = result['city']
			typ = result['type']
			dom_hand = result["dom_hand"]
			club = result["club"]
			status = result["status"]
			timestamp = result['timestamp']
			_id = str(result["_id"])
			url =''
			for file in glob.glob("static/images/*.*"):
				if _id in file:
					url=file


			if status == 0:
				return jsonify({"response":"deactivated"})
			if pbkdf2_sha256.verify(password, phash) is True:
				return jsonify({"response":"ok","name":name,"city":city,"type":typ,"timestamp":timestamp,"dom_hand":dom_hand,"club":club,"image_url":url})
			else:
				return jsonify({"response":"unauthorized"})			
		except TypeError as e:
			print(e)
			return jsonify({"response":"unexistent"})





	def deactivate_coach(self,username):
		try:
			mres = {"_id":username}
			newv = {"$set":{"status":0}}
			self.mongo.update_one(mres,newv)		
			return jsonify({"response":"deactivated"})	
		except TypeError:
			return jsonify({"response":"unexistent"})





	def activate_coach(self,username):
		try:
			mres = {"_id":username}
			newv = {"$set":{"status":1}}
			self.mongo.update_one(mres,newv)		
			return jsonify({"response":"activated"})	
		except TypeError:
			return jsonify({"response":"unexistent"})





	def update_name(self,username,name):
		try:
			mres = {"_id":username}
			newv = {"$set":{"coach_name":name}}
			self.mongo.update_one(mres,newv)		
			return jsonify({"response":"updated"})	
		except TypeError:
			return jsonify({"response":"unexistent"})





	def update_password(self,username,password):
		try:
			phash = pbkdf2_sha256.hash(password)
			mres = {"_id":username}
			newv = {"$set":{"coach_password":phash}}
			self.mongo.update_one(mres,newv)		
			return jsonify({"response":"updated"})	
		except TypeError:
			return jsonify({"response":"unexistent"})




	def update_email(self,username,email):
		try:
			mres = {"_id":username}
			newv = {"$set":{"email":email}}
			self.mongo.update_one(mres,newv)		
			return jsonify({"response":"updated"})	
		except TypeError:
			return jsonify({"response":"unexistent"})



	def update_address(self,username,address):
		try:
			mres = {"_id":username}
			newv = {"$set":{"address":address}}
			self.mongo.update_one(mres,newv)		
			return jsonify({"response":"updated"})	
		except TypeError:
			return jsonify({"response":"unexistent"})



	def update_city(self,username,city):
		try:
			mres = {"_id":username}
			newv = {"$set":{"city":city}}
			self.mongo.update_one(mres,newv)		
			return jsonify({"response":"updated"})	
		except TypeError:
			return jsonify({"response":"unexistent"})



	def update_country(self,username,country):
		try:
			mres = {"_id":username}
			newv = {"$set":{"country":country}}
			self.mongo.update_one(mres,newv)		
			return jsonify({"response":"updated"})	
		except TypeError:
			return jsonify({"response":"unexistent"})



	def update_birthday(self,username,phone):
		try:
			mres = {"_id":username}
			newv = {"$set":{"phone":phone}}
			self.mongo.update_one(mres,newv)		
			return jsonify({"response":"updated"})	
		except TypeError:
			return jsonify({"response":"unexistent"})



	def update_phone(self,username,birthday):
		try:
			mres = {"_id":username}
			newv = {"$set":{"birthday":birthday}}
			self.mongo.update_one(mres,newv)		
			return jsonify({"response":"updated"})	
		except TypeError:
			return jsonify({"response":"unexistent"})


	def update_image(self,username,image,app):
		try:
			extension = secure_filename(image.filename).split('.')[-1]
			image.save(os.path.join(app.config['UPLOAD_FOLDER'],username+'.' +extension))
			return jsonify({"response":"updated"})	
		except Exception as e:
			return jsonify({"response":str(e)})





	def register_player_for_coach(self,name,coach_username):
		try:
			result = self.mongo.find_one({"_id":coach_username})
			typ = result['type']
			status = result["status"]

			if status == 0:
				return jsonify({"response":"deactivated"})
			if int(typ) == 0:
				player_dic ={"_id":name,"coach_username":coach_username,"timestamp":datetime.datetime.now()}
				self.players.insert_one(player_dic)
				return jsonify({"response":"added"})
			else:
				return jsonify({"response":"player_account_not_allowed"})

		except pymongo.errors.DuplicateKeyError:
			return jsonify({"response":"duplicate"})
		except TypeError:
			return jsonify({"response":"unexistent"})




	def delete_player_for_coach(self,name):
		try:
			result = self.players.find_one({"_id":name})
			coach_username = result["coach_username"]
			timestamp = result["timestamp"]

			res = self.mongo.find_one({"_id":coach_username})
			typ = res['type']
			
			if int(typ) == 0:
				self.players.delete_one({"_id":name})
				return jsonify({"response":"deleted"})
			else:
				return jsonify({"response":"player_account_not_allowed"})
		except TypeError as e:
			print(e)
			return jsonify({"response":"unexistent"})



	def show_players_for_coach(self,coach_username):
		try:
			result = self.players.find({"coach_username":coach_username})
			res = self.mongo.find_one({"_id":coach_username})
			status = res['status']
			
			if status == 0:
				return jsonify({"response":"deactivated"})
			else:
				return dumps(result)
		except TypeError as e:
			print(e)
			return jsonify({"response":"unexistent"})



	




