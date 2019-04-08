import numpy as np
import os
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile
import cv2
from collections import defaultdict
from io import StringIO
from matplotlib import pyplot as plt
from PIL import Image
import os

# This is needed since the notebook is stored in the object_detection folder.
sys.path.append("/home/phoenix/Documents/models-master/research")
sys.path.append("/home/phoenix/Documents/models-master/research/slim")
print(os.system("protoc object_detection/protos/*.proto --python_out=."))


from object_detection.utils import ops as utils_ops
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util


class Court_Frame:

	def __init__(self):
		# Path to frozen detection graph. This is the actual model that is used for the object detection.
		self.PATH_TO_FROZEN_GRAPH = 'IG/frozen_inference_graph.pb'
		# List of the strings that is used to add correct label for each box.
		self.PATH_TO_LABELS = 'label.pbtxt'


		self.detection_graph = tf.Graph()
		with self.detection_graph.as_default():
			od_graph_def = tf.GraphDef()
			with tf.gfile.GFile(self.PATH_TO_FROZEN_GRAPH, 'rb') as fid:
				serialized_graph = fid.read()
				od_graph_def.ParseFromString(serialized_graph)
				tf.import_graph_def(od_graph_def, name='')

		self.label_map = label_map_util.load_labelmap(self.PATH_TO_LABELS)
		self.categories = label_map_util.convert_label_map_to_categories(self.label_map, max_num_classes=1, use_display_name=True)
		self.category_index = label_map_util.create_category_index(self.categories)



	def run_inference_for_single_image(self,image, graph):
	    with graph.as_default():
	        with tf.Session() as sess:
	        # Get handles to input and output tensors
	            ops = tf.get_default_graph().get_operations()
	            all_tensor_names = {output.name for op in ops for output in op.outputs}
	            tensor_dict = {}
	            for key in ['num_detections', 'detection_boxes', 'detection_scores','detection_classes', 'detection_masks']:
	                tensor_name = key + ':0'
	                if tensor_name in all_tensor_names:
	                    tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(tensor_name)

	            if 'detection_masks' in tensor_dict:
	                # The following processing is only for single image
	                detection_boxes = tf.squeeze(tensor_dict['detection_boxes'], [0])
	                detection_masks = tf.squeeze(tensor_dict['detection_masks'], [0])
	                # Reframe is required to translate mask from box coordinates to image coordinates and fit the image size.
	                real_num_detection = tf.cast(tensor_dict['num_detections'][0], tf.int32)
	                detection_boxes = tf.slice(detection_boxes, [0, 0], [real_num_detection, -1])
	                detection_masks = tf.slice(detection_masks, [0, 0, 0], [real_num_detection, -1, -1])
	                detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
	                    detection_masks, detection_boxes, image.shape[0], image.shape[1])
	                detection_masks_reframed = tf.cast(
	                    tf.greater(detection_masks_reframed, 0.5), tf.uint8)
	                # Follow the convention by adding back the batch dimension
	                tensor_dict['detection_masks'] = tf.expand_dims(
	                    detection_masks_reframed, 0)
	            
	            
	            
	            image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')

	            # Run inference
	            output_dict = sess.run(tensor_dict,
	                                 feed_dict={image_tensor: np.expand_dims(image, 0)})

	            # all outputs are float32 numpy arrays, so convert types as appropriate
	            output_dict['num_detections'] = int(output_dict['num_detections'][0])
	            output_dict['detection_classes'] = output_dict['detection_classes'][0]
	            output_dict['detection_masks'] = output_dict['detection_masks'][0]
	        return output_dict




	def imfill(inp):
	    im_th=inp

	    # Copy the thresholded image.
	    im_floodfill = im_th.copy()
	   # Mask used to flood filling.
	    # Notice the size needs to be 2 pixels than the image.
	    h, w = im_th.shape[:2]
	    mask = np.zeros((h+2, w+2), np.uint8)

	    # Floodfill from point (0, 0)
	    cv2.floodFill(im_floodfill, mask, (0,0), 255);
	    
	    # Invert floodfilled image
	    im_floodfill_inv = cv2.bitwise_not(im_floodfill)
	    # Combine the two images to get the foreground.
	    im_out = im_th | im_floodfill_inv
	    return im_out



	def find_court(self,image_np):
	    image_np = cv2.resize(image_np,(512,384))
	    # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
	    image_np_expanded = np.expand_dims(image_np, axis=0)
	    
	    # Actual detection.
	    output_dict = self.run_inference_for_single_image(image_np, self.detection_graph)

	    mask=output_dict['detection_masks'][0]
	    print(mask.shape)
	    ret, mask = cv2.threshold(mask, 0, 255, cv2.THRESH_BINARY)
	    mask=Court_Frame.imfill(mask)
	    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
	    
	    length = len(contours)
	    #concatinate points form all shapes into one array
	    cont = np.vstack(contours)
	    hull = cv2.convexHull(cont)
	     
	    uni_hull = []
	    uni_hull.append(hull)
	    return uni_hull    	





