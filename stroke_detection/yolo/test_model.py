from keras.models import load_model
import cv2
from yolo.yolo_opencv_cl import YOLO
import numpy as np
from keras.models import model_from_json
from keras.applications.vgg16 import preprocess_input
from yolo.decode import Decode
import tensorflow as tf 
import threading
from bson.objectid import ObjectId
import pymongo



class StrokeDetectionModel:
	def __init__(self):
		json_file = open('yolo/model.json', 'r')
		loaded_model_json = json_file.read()
		json_file.close()
		self.loaded_model = model_from_json(loaded_model_json)
		self.loaded_model.load_weights("yolo/weights.total.hdf5")
		self.graph =tf.get_default_graph()
		myclient = pymongo.MongoClient("mongodb://localhost:27017/")
		mydb = myclient["orla"]
		self.matches = mydb["matches"]

	def start(self,files,object_id):
		t1 = threading.Thread(target=self.serve_results, args=[files,object_id])
		t1.start()

	def serve_results(self,files,object_id):
		shots_list = list()
		shots_history = list()
		for file in files:
			print(file)
			im = cv2.imread(file)
			im = YOLO.player_track(im)
			img=None
			try:
				img = cv2.cvtColor(im[1],cv2.COLOR_BGR2RGB)
			except:
				img = np.zeros((224,224,3))
				print("error")
			print(img.shape)
			inp =np.array([img])
			inp=inp.astype(np.float32)
			inp = preprocess_input(inp)
			print(inp.shape)
			out = list()
			with self.graph.as_default():
				out = list(self.loaded_model.predict(inp)[0])

			shots_list.append(out.index(max(out)))
			shots_list = shots_list[-5:]
			shot = max(set(shots_list), key=shots_list.count)
			shot_index = 3
			if(shots_list.count(shot)>=3):
				shot_index = shot

			if shot_index==0:
				cv2.putText(im[0],"forehand", (100,100), cv2.FONT_HERSHEY_SIMPLEX, 3, 255,2)

			elif shot_index==1:
				cv2.putText(im[0],"backhand", (100,100), cv2.FONT_HERSHEY_SIMPLEX, 3, 255,2)

			elif shot_index==2:
				cv2.putText(im[0],"serve", (100,100), cv2.FONT_HERSHEY_SIMPLEX, 3, 255,2)

			else:
				cv2.putText(im[0],"idle", (100,100), cv2.FONT_HERSHEY_SIMPLEX, 3, 255,2)

			shots_history.append(shot_index)
		ans_dict = Decode.frames_analyze(shots_history)
		self.matches.update({"_id": ObjectId(object_id)}, {"$set": {"number_of_shots": ans_dict["number_of_shots"], "number_of_backhands": ans_dict["number_of_backhands"], "number_of_forehands": ans_dict["number_of_forehands"], "number_of_serves": ans_dict["number_of_serves"],"serves": ans_dict["serves"],"forehands": ans_dict["forehands"],"backhands": ans_dict["backhands"]}})
#3980
#4550

#5450
#5800