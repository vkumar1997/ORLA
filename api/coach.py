from flask import jsonify
import pymongo
from passlib.hash import pbkdf2_sha256
from werkzeug import secure_filename
import os
import datetime
from bson.json_util import dumps
import glob
import shutil

class Coach:
	def __init__(self):
		myclient = pymongo.MongoClient("mongodb://localhost:27017/")
		mydb = myclient["orla"]
		self.mongo = mydb["coaches"]
		self.players = mydb["players"]
		self.mongo.create_index("email_id",unique=True)
		

	def register_coach(self,password,name,email,city,dom_hand,club,image,typ,app):
		try:
			phash = pbkdf2_sha256.hash(password)
			dic = { "email_id": email, "coach_password": phash,"city":city,"coach_name": name, "type":typ, "club":club, "status": 1,"timestamp":datetime.datetime.now()}
			x = self.mongo.insert_one(dic)
			extension = secure_filename(image.filename).split('.')[-1]
			username = str(x.inserted_id)
			image.save(os.path.join(app.config['UPLOAD_FOLDER'], username+'.' +extension))
			player_dic ={"name":name,"dom_hand":dom_hand,"coach_username":x.inserted_id,"timestamp":datetime.datetime.now()}
			x = self.players.insert_one(player_dic)
			if int(typ) == 0:
				usernamez = str(x.inserted_id)
				src = os.path.join(app.config['UPLOAD_FOLDER'],username+'.' +extension)
				dst = os.path.join(app.config['UPLOAD_FOLDER'],"pl_" + usernamez+'.' +extension)
				shutil.copy2(src,dst)
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
			club = result["club"]
			status = result["status"]
			timestamp = result['timestamp']
			_id = str(result["_id"])
			url =''
			for file in glob.glob("static/images/*.*"):
				if _id in file:
					url=file


			if int(status) == 0:
				return jsonify({"response":"deactivated"})
			if pbkdf2_sha256.verify(password, phash) is True:
				return jsonify({"response":"ok","name":name,"city":city,"type":typ,"timestamp":timestamp,"club":club,"image_url":url})
			else:
				return jsonify({"response":"unauthorized"})			
		except TypeError as e:
			print(e)
			return jsonify({"response":"unexistent"})



	def register_player_for_coach(self,name,dom_hand,coach_mail,image,app):
		try:
			result = self.mongo.find_one({"email_id":coach_mail})
			typ = result['type']
			status = result["status"]

			if int(status) == 0:
				return jsonify({"response":"deactivated"})
			if int(typ) == 0:
				player_dic ={"name":name,"dom_hand":dom_hand,"coach_username":result["_id"],"timestamp":datetime.datetime.now()}
				x = self.players.insert_one(player_dic)
				username = "pl_" + str(x.inserted_id)
				extension = secure_filename(image.filename).split('.')[-1]
				image.save(os.path.join(app.config['UPLOAD_FOLDER'],username+'.' +extension))
				return jsonify({"response":"added"})
			else:
				return jsonify({"response":"player_account_not_allowed"})

		except pymongo.errors.DuplicateKeyError:
			return jsonify({"response":"duplicate"})
		except TypeError as e:
			print(e)
			return jsonify({"response":"unexistent"})


	def show_players(self,coach_mail):
		try:
			res = self.mongo.find_one({"email_id":coach_mail})
			result = self.players.find({"coach_username":res['_id']})
			status = res['status']
			typ = res['type']
			print(typ)
			if int(status) == 0:
				return jsonify({"response":"deactivated"})
			else:
				if int(typ)==0:
					json_list=[]
					for r in result:
						_id = r["_id"]
						name = r["name"]
						dom_hand = r["dom_hand"]
						timestamp = r["timestamp"]
						url =''
						for file in glob.glob("static/images/*.*"):
							if 'pl_' + str(_id) in file:
								url=file

						json_list.append({"_id":str(_id),"url":url,"name":name,"dom_hand":dom_hand,"timestamp":timestamp})
					return jsonify({"response":json_list})

				else:
					return jsonify({"response":"player_account_not_allowed"})	
		except TypeError as e:
			print(e)
			return jsonify({"response":"unexistent"})





	
	


	




