from os import walk
from pathlib import Path

import podcasts
import episodes
import os
import console
import psutil

INDENT_LEFT_SIDE = "                          "
DIV_TO_GB = 1_073_741_824 #2^30
CGREY    = '\33[90m'
CBOLD     = '\33[1m'
CEND      = '\33[0m'

def every_choice(dl_every):
	if dl_every:
		return CBOLD + "E > EVERY episode downloaded" + CEND
	else:
		return CGREY + "E > EVERY episode downloaded" + CEND

def old_choice(dl_every, dl_number_str, dl_oldest):
	if dl_number_str=="1":
		episodes_word = " episode "
	else:
		episodes_word = " episodes "
	if dl_every:
		return CGREY + "O > OLD " + dl_number_str + episodes_word + "first" + CEND
	elif dl_oldest:
		return CBOLD + "O > OLD " + dl_number_str + episodes_word + "first"+  CEND 
	else:
		return CGREY + "O > OLD " + dl_number_str + episodes_word + "first" + CEND

def new_choice(dl_every, dl_number_str, dl_oldest):
	if dl_number_str=="1":
		episodes_word = " episode "
	else:
		episodes_word = " episodes "
	if dl_every:
		return CGREY + "N > NEW " + dl_number_str + episodes_word + "first" + CEND
	elif dl_oldest:
		return CGREY + "N > NEW " + dl_number_str + episodes_word + "first" + CEND
	else:
		return CBOLD + "N > NEW " + dl_number_str + episodes_word + "first" + CEND

def alpha_choices(dl_every, dl_number_str, dl_oldest):
	every_text = every_choice(dl_every)
	old_text = old_choice(dl_every, dl_number_str, dl_oldest)
	new_text = new_choice(dl_every, dl_number_str, dl_oldest)
	#print("\n\n\n")
	print("A >  ADD a podcast                Q > QUIT program    " + every_text)        
	print("C > CHANGE podcast url            H > HELP            " + old_text ) 
	print("D > DELETE podcast        Control-C > KILL program    " + new_text) 
	print("R > RENAME podcast")    

def free_gb():
	bytes_free = psutil.disk_usage(".").free
	gb_free = bytes_free / DIV_TO_GB
	gb_2_dec = f"{gb_free:.2f}"
	free_str = str(gb_2_dec)
	return free_str

def choices_mess(dl_every, dl_number, dl_oldest):
	if dl_number==1:
		episodes_word = "episode"
	else:
		episodes_word = "episodes"
	gb_free = INDENT_LEFT_SIDE + free_gb() + "GB free ---- "
	if dl_every:
		return f"{gb_free}Get every episode"
	elif dl_oldest:
		return f"{gb_free}Get oldest {dl_number} {episodes_word}"
	else:
		return f"{gb_free}Get newest {dl_number} {episodes_word}"

def user_choice():
	menu_choice = input("Command(A-R) or podcast # : ")
	lower_choice = menu_choice.lower()
	return lower_choice

def show_choices(dl_every, dl_number, dl_oldest):
	alpha_choices(dl_every, str(dl_number), dl_oldest)
	dirs_files = alive_pods()
	get_mess = choices_mess(dl_every, dl_number, dl_oldest)
	print(get_mess)
	(podcast_list, folder_to_all_items) = podcast_choices()
	for a_choice in podcast_list:
		print(a_choice)
	return folder_to_all_items

def show_choose(menu_choice, dl_every, dl_number, dl_oldest, folder_to_all_items):
	quit_menu = False
	match menu_choice:
		case "a":
			podcasts.add_folder()
		case "c":
			print("C")
		case "d":
			print("D")
		case "r":
			print("r")
		case "e":
			dl_every = True
		case "o":
			dl_every = False
			dl_oldest = True
			dl_number = fig_num('OLDEST')
		case "n":
			dl_every = False
			dl_oldest = False
			dl_number = fig_num('NEWEST')
		case "q":
			quit_menu = True
		case "h":
			print("HELP ..... ")
		case _:
			print(INDENT_LEFT_SIDE + "To download podcasts quickly, Keep this program active, in focus")
			number_choice(menu_choice, dl_every, dl_number, dl_oldest, folder_to_all_items)
	menu_data = (dl_every, dl_number, dl_oldest, quit_menu)
	return menu_data

def fig_num(old_or_new):
	limit_number = 'Number of ' + old_or_new +' episodes to download: '
	number_str = input(limit_number)
	try:
		dl_number = int(number_str)
		if dl_number<1:
			dl_number = 1
	except Exception as e:
		#print("fig_num EX", str(e))
		dl_number = 1
	return dl_number

def alive_pods():
	cur_dir = Path.cwd()
	alive_pods = []
	for (dirpath, dirnames, filenames) in walk(cur_dir):
		for a_dir in dirnames:
			pos_rss_file = os.path.join(cur_dir, a_dir, podcasts.RSS_FILE_NAME)
			rss_file = Path(pos_rss_file)
			if rss_file.is_file():
				alive_pods.append(a_dir)
		break
	return alive_pods

def epi_nums(dirs_files):
	numbered_pods =[]
	folder_to_all_items = {}
	cur_dir = Path.cwd()
	for idx, a_dir in enumerate(dirs_files):
		dir_stat = '... ' + str(idx+1) + ' Reading ' + a_dir + ' ...'
		console.read_folder(dir_stat)
		
		all_episodes = episodes.get_items(a_dir)
		folder_to_all_items[a_dir] = all_episodes

		cur_epis = len(all_episodes)
		rss_folder = os.path.join(cur_dir, a_dir)
		_, _, files = next(os.walk(rss_folder))
		have_count = len(files) -1
		index = idx+1
		pod_menu = f"{index} - {a_dir} ({have_count}/{cur_epis})"
		numbered_pods.append(pod_menu)
	console.read_folder('')
	return (numbered_pods, folder_to_all_items)

def podcast_choices():
	dirs_files = alive_pods()
	(numbered_pods, folder_to_all_items) = epi_nums(dirs_files)
	podcast_list = []
	for a_choice in numbered_pods:
		podcast_list.append(a_choice)
	return (podcast_list, folder_to_all_items)

def number_choice(menu_choice, dl_every, dl_number, dl_oldest, folder_to_all_items):
	print("")
	dirs_files = alive_pods()
	number_pods = len(dirs_files)
	try:
		rss_choice = int(menu_choice)
		if rss_choice<1 or rss_choice>number_pods:
			print("outside range", menu_choice)
		else:
			try:
				dirs_files = alive_pods()
				dir_name = dirs_files[rss_choice-1]
				all_episodes = folder_to_all_items[dir_name]
				episodes.update_folder(dir_name, dl_every, dl_number, dl_oldest, all_episodes)
			except Exception as e:
				print("File Error", str(e))
	except Exception as e:
		print("not valid integer", menu_choice)
