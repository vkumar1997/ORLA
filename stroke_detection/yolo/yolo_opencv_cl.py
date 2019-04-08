import cv2
import argparse
import numpy as np



class YOLO:
	config = "yolo/yolov3.cfg"
	weights = "yolo/yolov3.weights"
	txt = "yolo/yolov3.txt"

	def get_output_layers(net):	    
	    layer_names = net.getLayerNames()
	    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
	    return output_layers


	def draw_prediction(classes,COLORS,img, class_id, confidence, x, y, x_plus_w, y_plus_h):
		if classes[class_id] in ['person','tennis racket','sports ball']: 
		    label = str(classes[class_id])
		    color = COLORS[class_id]
		    cv2.rectangle(img, (x,y), (x_plus_w,y_plus_h), color, 2)
		    cv2.putText(img, label, (x-10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
		    '''cv2.imshow('ig',img)
		    cv2.waitKey(0)'''


	def point_lie(x,y,w,h,xc,yc):
		if xc>x and xc<x+w and yc>y and yc<y+h:
			return True
		return False

	def overlap(x1,y1,w1,h1,x2,y2,w2,h2):
		if YOLO.point_lie(x1,y1,w1,h1,x2,y2) is True:
			return True
		if YOLO.point_lie(x1,y1,w1,h1,x2,y2+h2) is True:
			return True
		if YOLO.point_lie(x1,y1,w1,h1,x2+w2,y2) is True:
			return True
		if YOLO.point_lie(x1,y1,w1,h1,x2+w2,y2+h2) is True:
			return True	

	def player_track(image):
		try:
			Width = image.shape[1]
			Height = image.shape[0]
			scale = 0.00392
			classes = None
			with open(YOLO.txt, 'r') as f:
				classes = [line.strip() for line in f.readlines()]
			COLORS = np.random.uniform(0, 255, size=(len(classes), 3))
			net = cv2.dnn.readNet(YOLO.weights, YOLO.config)
			blob = cv2.dnn.blobFromImage(image, scale, (416,416), (0,0,0), True, crop=False)
			net.setInput(blob)
			outs = net.forward(YOLO.get_output_layers(net))

			class_ids = []
			confidences = []
			boxes = []
			conf_threshold = 0.2
			nms_threshold = 0.4


			for out in outs:
				for detection in out:
					scores = detection[5:]
					class_id = np.argmax(scores)
					confidence = scores[class_id]
					if confidence > conf_threshold:
						center_x = int(detection[0] * Width)
						center_y = int(detection[1] * Height)
						w = int(detection[2] * Width)
						h = int(detection[3] * Height)
						x = center_x - w / 2
						y = center_y - h / 2
						class_ids.append(class_id)
						confidences.append(float(confidence))
						boxes.append([x, y, w, h])

		
			indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)
			person_rectangle = list()
			t_rectangle = list()
			for i in indices:
				i = i[0]
				box = boxes[i]
				x = box[0]
				y = box[1]
				w = box[2]
				h = box[3]
				if classes[class_ids[i]] in ['tennis racket']:
						t_rectangle.append([x,y,w,h])

				if classes[class_ids[i]] in ['person']:
						person_rectangle.append([x,y,w,h])
					
			largest_area = Width * Height * 0.004
			largest_rectangle = None
			for rectangle in person_rectangle:
				if rectangle[2]*rectangle[3] > largest_area and rectangle[2]<0.7*Width:
					largest_area = rectangle[2]*rectangle[3]
					largest_rectangle = rectangle
			
			tennis_rectangle =None
			if largest_rectangle is not None:
				for rec in t_rectangle:
					if YOLO.overlap(largest_rectangle[0],largest_rectangle[1],largest_rectangle[2],largest_rectangle[3],rec[0],rec[1],rec[2],rec[3]):
						tennis_rectangle = rec
						break


			if largest_rectangle is not None:
				if tennis_rectangle is not None:
					x = min(int(largest_rectangle[0]),int(tennis_rectangle[0]))
					y = min(int(largest_rectangle[1]),int(tennis_rectangle[1]))
					xw = max(int(largest_rectangle[0])+int(largest_rectangle[2]),int(tennis_rectangle[0])+int(tennis_rectangle[2]))
					yh = max(int(largest_rectangle[1])+int(largest_rectangle[3]),int(tennis_rectangle[1])+int(tennis_rectangle[3]))
					
					x = max(x,0)
					y = max(y,0)
					xw = min(xw,Width-1)
					yh = min(yh,Height-1)
					ar = image[y:yh,x:xw]
					crop_img =np.empty_like(ar)
					np.copyto(crop_img,ar)
					
				else:
					x = max(int(largest_rectangle[0]),0)
					y = max(int(largest_rectangle[1]),0)
					xw = min(int(x+int(largest_rectangle[2])),Width-1)
					yh = min(int(y+int(largest_rectangle[3])),Height-1)
					ar = image[y:yh,x:xw]
					crop_img =np.empty_like(ar)
					crop_img[:]  = ar

				

			else:
				return image,np.zeros((224,224,3))
				
				#return cv2.resize(img,(224,224))

			
				
			img = image.copy()
			for i in indices:
				i = i[0]
			    
				box = boxes[i]
				x = box[0]
				y = box[1]
				w = box[2]
				h = box[3]
				YOLO.draw_prediction(classes,COLORS,img, class_ids[i], confidences[i], round(x), round(y), round(x+w), round(y+h))
			
			crop_img = cv2.resize(crop_img,(224,224))
			return img,crop_img

		except Exception as e:
			print(e)
			return image,np.zeros((224,224,3))
'''
import glob

for file in glob.glob("forehand/*.jpeg"):
	filename = file.split("/")[-1]
	print(file)
	im = cv2.imread(file)
	res = YOLO.player_track(im)
	cv2.imshow('im',res[0])
	cv2.waitKey(1)
	result = cv2.resize(res[1],(150,150))
	cv2.imshow('fm',result)
	cv2.waitKey(1)
	cv2.imwrite("frames/{0}".format(filename),result)

'''