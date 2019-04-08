import math
import cv2
import numpy as np
from court_frame import Court_Frame 












class background_subt:
	def subtract(path1,path2):
		img_a_color = cv2.imread(path1)
		img_a_color = cv2.resize(img_a_color,(854,480))
		img_b_color = cv2.imread(path2)
		img_b_color = cv2.resize(img_b_color,(854,480))
		
		img_a = cv2.cvtColor(img_a_color, cv2.COLOR_BGR2GRAY)
		img_b = cv2.cvtColor(img_b_color, cv2.COLOR_BGR2GRAY)
		
		height,width = img_a.shape
		
		for i in range(height):
			for j in range(width):
				x = int(img_a[i][j])
				y= int(img_b[i][j])
				if(abs(x-y)<30):
					img_b_color[i][j][:]=0

		gray_image = cv2.cvtColor(img_b_color, cv2.COLOR_BGR2GRAY)
		(thresh, im_bw2) = cv2.threshold(gray_image, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
		kernel = np.ones((5,5), np.uint8) 
		im_bw2 = cv2.dilate(im_bw2, kernel, iterations=1)
		im_bw2 = cv2.erode(im_bw2, kernel, iterations=1)
		contours, hierarchy =  cv2.findContours(im_bw2,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
		mask = np.ones(img_b_color.shape[:2], dtype="uint8") * 0
		for contour in contours:
			area = cv2.contourArea(contour)
			if 3<area<90:
				cv2.drawContours(mask, [contour], -1, 255, -1)

		final_rgb_mask = cv2.bitwise_and(img_b_color, img_b_color, mask=mask)
		'''cv2.imshow('mask',im_bw2)
		cv2.waitKey(0)
		cv2.imshow('mask',final_rgb_mask)
		cv2.waitKey(0)'''
		
		return final_rgb_mask













class HSVMask:
	def find(img_b_color):
		img_b_hsv = cv2.cvtColor(img_b_color,cv2.COLOR_BGR2HSV)
		mask = cv2.inRange(img_b_hsv,(0.11*255, 0.1*255, 0.1*255), (0.2*255, 255, 255))
		#cv2.imshow('mask',mask)
		#cv2.waitKey(0)
		
		return 	mask











class eccentricity:
	def find(img_b_color):
		img_b = cv2.cvtColor(img_b_color, cv2.COLOR_BGR2GRAY)
		
		(thresh, im_bw2) = cv2.threshold(img_b, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

		contours, hierarchy =  cv2.findContours(im_bw2,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
		mask = np.ones(img_b_color.shape[:2], dtype="uint8") * 0
		for contour in contours:
			area = cv2.contourArea(contour)
			perimeter = cv2.arcLength(contour,True)
			if not perimeter<5:
				circularity = 4*math.pi*(area/(perimeter*perimeter))
				if 0.4<circularity<1.2:
					cv2.drawContours(mask, [contour], -1, 255, -1)

		
		final_rgb_mask = cv2.bitwise_and(img_b_color, img_b_color, mask=mask)

		img_b_hsv = cv2.cvtColor(final_rgb_mask,cv2.COLOR_BGR2HSV)
		final_mask = cv2.inRange(img_b_hsv,(0.11*255, 0.0*255, 0.1*255), (0.3*255, 255, 255) )
		#cv2.imshow('mask',final_rgb_mask)
		#cv2.waitKey(0)
		return final_mask







class Harris:
	def find(img_b_color,orig):
		img_b_hsv = cv2.cvtColor(img_b_color,cv2.COLOR_BGR2HSV)
		mask = cv2.inRange(img_b_hsv,(0.11*255, 0.0*255, 0.1*255), (0.3*255, 255, 255) )
		gray_mask = cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY)
		gray_mask=np.float32(gray_mask)
		blocksize=2
		ksize=3
		k=0.0004
		dst = cv2.cornerHarris(gray_mask,blocksize,ksize,k)
		
		height,width = mask.shape

		
		for i in range(height):
			for j in range(width):
				x = int(mask[i][j])
				y = int(dst[i][j])
				if x>0 and y>0:
					mask[i][j]=255
		
		#cv2.imshow('mask',mask)
		#cv2.waitKey(0)
		
		return mask
		







class Update:
	def __init__(self):
		self.rois = list()
		self.link = list()
		self.frame_number = 0

	def add_new_roi(self,contour):
		self.rois.append(contour)
		self.link.append([0,None,-1,1000])

	def delete_obsolete_roi(self,index):
		self.rois.pop(index)
		self.link.pop(index)

	def find_center(self,contour):
		M = cv2.moments(contour)
		cX = int(M["m10"] / M["m00"])
		cY = int(M["m01"] / M["m00"])
		return cX,cY


	def eucildean(self,x1,y1,x2,y2):
		x = x2-x1
		y = y2-y1
		sum = math.pow(x,2) +math.pow(y,2)
		return math.sqrt(sum)


	def update_all_rois(self,combined_mask):
		self.frame_number = self.frame_number + 1
		contours, hierarchy =  cv2.findContours(combined_mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)
		for contour in contours:
			flag=True
			for value in self.rois:
				all_vals = np.concatenate([value,contour])
				unique = np.unique(all_vals,axis=0)
				overlap = len(unique)/len(all_vals)
				if overlap <= 0.95:
					flag = False

			if flag is True:
				self.check_for_links(contour)
				self.add_new_roi(contour)

		self.update_nums()
		return self.return_updated_mask(self.rois)


	def check_for_links(self,contour):
		for i in range(len(self.rois)):
			if self.link[i][1] is None or self.frame_number==self.link[i][2]:
				x1,y1 = self.find_center(self.rois[i])
				x2,y2 = self.find_center(contour)
				distance = self.eucildean(x1,y1,x2,y2)
				if distance<40 and distance<self.link[i][3]:
					self.link[i][0]=101
					self.link[i][1]=contour
					self.link[i][2]=self.frame_number
					self.link[i][3]=distance



	def update_nums(self):
		delete_indexes = list()
		for i in range(len(self.link)):
			self.link[i][0] = self.link[i][0]+1
			if(100>=self.link[i][0]>=5):
				delete_indexes.append(i)

		delete_indexes.sort(reverse=True)
		for index in delete_indexes:
			self.delete_obsolete_roi(index)
			
	def return_updated_mask(self,lst):
		updated_mask = np.ones((384,512), dtype="uint8") * 0
		cv2.drawContours(updated_mask, lst, -1, 255, -1)
		return updated_mask

	def update_image(updated_mask,orig,time,name):
		grey_3_channel = cv2.cvtColor(updated_mask, cv2.COLOR_GRAY2BGR)
		grey_3_channel = cv2.resize(grey_3_channel,(512,384))
		orig = cv2.resize(orig,(512,384))
		numpy_horizontal = np.hstack((orig, grey_3_channel))
		cv2.imshow(name,numpy_horizontal)
		cv2.waitKey(time)


	def find_longest_roi_chain(self):
		longest_chain = list()
		for  i in range(len(self.link)):
			chain = list()
			chain.append([self.rois[i],i])
			contour = self.link[i][1]
			while True:
				if contour is None:
					break
				else:
					ix = -1 
					for j in range(len(self.rois)):
						if np.array_equal(contour,self.rois[j]):
							ix=j
							break

					if not ix==-1:
						chain.append([contour,ix])
						if(len(chain)>len(longest_chain)):
							longest_chain=chain
						contour = self.link[ix][1]
					else:
						break
					
		return longest_chain					




class masks:
	def find_ball(update,path1,path2):
		img_b_color = background_subt.subtract(path1,path2)
		orig = cv2.imread(path2)
		orig = cv2.resize(orig,(854,480))
				
		mask1 = HSVMask.find(img_b_color)
		mask2 = eccentricity.find(img_b_color)
		mask3 = Harris.find(img_b_color,orig)

		inter_mask = cv2.bitwise_and(mask1,mask2)
		combined_mask = cv2.bitwise_and(inter_mask,mask3)
		combined_mask=inter_mask
		
		contours, hierarchy =  cv2.findContours(combined_mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
		if(len(contours)==0):
			combined_mask = cv2.bitwise_and(mask1,mask2)
			contours, hierarchy =  cv2.findContours(combined_mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
			if(len(contours)==0):
				inter_mask = cv2.bitwise_or(cv2.bitwise_and(mask1,mask2),cv2.bitwise_and(mask2,mask3))
				combined_mask = cv2.bitwise_or(inter_mask,cv2.bitwise_and(mask1,mask3))
				combined_mask=cv2.bitwise_and(mask2,mask3)
				

		kernel = np.ones((3,3), np.uint8) 
		combined_mask = cv2.dilate(combined_mask, kernel, iterations=1)	
		combined_mask = cv2.resize(combined_mask,(512,384))
		
		updated_mask = update.update_all_rois(combined_mask)
		Update.update_image(updated_mask,orig,1,'intermediate')

	
	def find_angle(x1,y1,x2,y2,x3,y3):
		a = np.array([x1,y1])
		b = np.array([x2,y2])
		c = np.array([x3,y3])
		ba = a - b
		bc = c - b
		cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
		angle = np.arccos(cosine_angle)
		print(np.degrees(angle))
		return np.degrees(angle)

		
		
	def find_landing_spot(longest_roi_chain):
		smallest_angle = 1000
		for index in range(len(longest_roi_chain)):
			try:
				x1,y1 = masks.find_center(longest_roi_chain[index][0])
				x2,y2 = masks.find_center(longest_roi_chain[index+1][0])
				x3,y3 = masks.find_center(longest_roi_chain[index+2][0])
				angle = masks.find_angle(x1,y1,x2,y2,x3,y3)
				if 7<angle<140 and angle<smallest_angle:
					small_angle_index = index
					return small_angle_index
			except:
				pass



	def find_center(contour):
		M = cv2.moments(contour)
		cX = int(M["m10"] / M["m00"])
		cY = int(M["m01"] / M["m00"])
		return cX,cY


		




class start:
	def run_frames(source,start_frame,end_frame,frame_gap):
		start2 = start_frame+4
		height = 384
		width = 512
		update = Update()
		orig=None

		while start_frame<end_frame:
			path1='../dataset2/{0}{1}.jpeg'.format(source,start_frame)
			path2='../dataset2/{0}{1}.jpeg'.format(source,start2)
			orig = cv2.imread(path2)
			masks.find_ball(update,path1,path2)
			start_frame=start_frame+frame_gap
			start2=start2+frame_gap

		longest_roi_chain = update.find_longest_roi_chain()
		lrc = [x[0] for x in longest_roi_chain]
		updated_mask = update.return_updated_mask(lrc)
		cv2.destroyAllWindows()
		Update.update_image(updated_mask,orig,0,'final')
		smallest_angle_index = masks.find_landing_spot(longest_roi_chain)
		print(smallest_angle_index)
		try:
			landing_contour = lrc[smallest_angle_index+1]
			court_frame = Court_Frame()
			mask = start.court_mask(orig,landing_contour)
			cv2.destroyAllWindows()
			Update.update_image(mask,orig,0,'final')
		except:
			print("Outside")

		
	def court_mask(orig,landing_contour):
		cf = Court_Frame()
		court_frame = np.ones((384,512), dtype="uint8") * 0
		court = cf.find_court(orig)
		cv2.drawContours(court_frame, court, -1, 255, 4)
		cv2.drawContours(court_frame, [landing_contour], -1, 255, -1)
		return court_frame




start.run_frames('test10_frame',1085,1098,1)
cv2.destroyAllWindows()
'''start.run_frames('test_frame',5946,5959,1)
cv2.destroyAllWindows()
start.run_frames('test2_frame',2937,2956,1)
cv2.destroyAllWindows()
start.run_frames('test_frame',21759,21800,2)
cv2.destroyAllWindows()'''
'''
start.run_frames('test_frame',400,443,2)
cv2.destroyAllWindows()
start.run_frames('test_frame',567,622,2)
cv2.destroyAllWindows()
start.run_frames('test_frame',3612,3670,2)
cv2.destroyAllWindows()
start.run_frames('test_frame',24282,24347,2)
cv2.destroyAllWindows()
start.run_frames('test2_frame',1759,1800,1)
cv2.destroyAllWindows()
start.run_frames('test2_frame',7595,7621,1)
cv2.destroyAllWindows()
start.run_frames('test2_frame',5548,5575,1)
cv2.destroyAllWindows()
start.run_frames('test2_frame',5697,5718,1)
cv2.destroyAllWindows()

'''


#400,443
#567,622
#3612,3670
#24282,24347

#1759,1800
#7595,7621
#5548,5575
#5697,#5718