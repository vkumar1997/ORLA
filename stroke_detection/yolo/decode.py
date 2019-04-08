class Decode:
	def frames_analyze(ls):
		confirmed_shots = [[],[],[]]
		ls = [str(i) for i in ls]
		ls = ''.join(ls)
		ls = ls.replace("3333333","xxxxxxx")
		frames=[]
		lock=False
		i=-1
		j=-1
		for k in range(len(ls)):
			if ls[k] is not 'x' and lock is False:
				i=k
				lock=True
			if (ls[k] is 'x' and lock is True) or (k == len(ls)-1 and lock is True):
				j=k-1
				lock=False
				frames.append((i+j)//2)

		ls = ls.split("xxxxxxx")
		while "" in ls:
			ls.remove("")

		for i in range(len(ls)):
			ls[i] = ls[i].replace("3","")

		for i,shot in enumerate(ls):
			frame_list = list(shot)
			shot_type = -1
			try:
				shot_type = max(shot)
			except:
				pass

			if int(shot_type)>=0 and frame_list.count(shot_type)>2:
				confirmed_shots[int(shot_type)].append(frames[i])


		number_of_shots = len(confirmed_shots[0])+len(confirmed_shots[1])+len(confirmed_shots[2])
		number_of_backhands = len(confirmed_shots[1])		
		number_of_forehands = len(confirmed_shots[0])
		number_of_serves = len(confirmed_shots[2])

		forehands = confirmed_shots[0]
		backhands = confirmed_shots[1]
		serves = confirmed_shots[2]
		answer_dict = {"number_of_shots":number_of_shots , "number_of_backhands":number_of_backhands, "number_of_forehands":number_of_forehands, "number_of_serves":number_of_serves, "forehands":forehands, "backhands":backhands, "serves":serves}
		return answer_dict

