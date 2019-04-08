from flask import jsonify
import pymongo
from passlib.hash import pbkdf2_sha256
import datetime
import glob
import os
from bson.json_util import dumps
from bson.objectid import ObjectId
from yolo.test_model import StrokeDetectionModel
stroke_detection_model=StrokeDetectionModel()

class Matches:
	def __init__(self):
		myclient = pymongo.MongoClient("mongodb://localhost:27017/")
		mydb = myclient["orla"]
		self.matches = mydb["matches"]
		self.players=mydb["players"]


	def register_match_for_player(self,player_username):
		try:
			self.players.find_one({"_id":player_username})
			player_dic ={"player_username":player_username,"timestamp":datetime.datetime.now()}
			_id = self.matches.insert_one(player_dic).inserted_id
			return jsonify({"response":"added","id":str(_id)})

		except pymongo.errors.DuplicateKeyError:
			return jsonify({"response":"duplicate"})
		except TypeError as e:
			print(e)
			return jsonify({"response":"unexistent"})
		except Exception as e:
			return jsonify({"response":"internal_server_error"})


	def delete_match_for_player(self,object_id):
		try:
			self.matches.delete_one({"_id":object_id})
			return jsonify({"response":"deleted"})

		except TypeError:
			return jsonify({"response":"unexistent"})



	def show_matches_for_player(self,player_username):
		try:
			result = self.matches.find({"player_username":player_username})
			self.players.find_one({"_id":player_username})
			json_list=[]
			for res in result:
				_id = res["_id"]
				player_username = res["player_username"]
				timestamp = res["timestamp"]
				json_list.append({"_id":str(_id),"player_username":player_username,"timestamp":timestamp})
			return jsonify({"response":json_list})
		except Exception as e:
			print(e)
			return jsonify({"response":"unexistent"})



	def start_processing(self,object_id):
		try:
			print(object_id)
			match = self.matches.find_one({"_id":ObjectId(object_id)})			
			search_dir = "static/images/{0}/1/".format(object_id)
			print(search_dir)
			files = list(filter(os.path.isfile, glob.glob(search_dir + "*.png")))
			files.sort(key=lambda x: os.path.getmtime(x))
			model = stroke_detection_model.start(files,object_id)
			#self.matches.update({"_id": ObjectId(object_id)}, {"$set": {"number_of_shots": 2}})
			return "done"
		except Exception as e:	
			print(e)
			return jsonify({"response":"unexistent"})



	def processing_results(self,object_id):
		try:
			match = self.matches.find_one({"_id":ObjectId(object_id)})	
		except Exception as e:	
			print(e)
			return jsonify({"response":"unexistent"})

		try:		
			print(match)
			_id =str(match["_id"])
			no_forehands = match["number_of_forehands"]
			no_backhands = match["number_of_backhands"]
			no_serves = match["number_of_serves"]
			forehands = match["forehands"]
			backhands = match["backhands"]
			serves = match["serves"]
			return jsonify({"no_forehands":no_forehands,"no_backhands":no_backhands,"no_serves":no_serves,"forehands":forehands,"backhands":backhands,"serves":serves})
		except Exception as e:
			return jsonify({"response":"unprocessed"})

