import podcasts
import episodes
import menu
import console

import os

def main():
	os.system('cls')
	dl_every = True
	dl_number = 1
	dl_oldest = True
	folder_to_all_items = {}
	while True:
		try:
			folder_to_all_items = menu.show_choices(dl_every, dl_number, dl_oldest)
			menu_choosen = menu.user_choice()
			menu_data =menu.show_choose(menu_choosen, dl_every, dl_number, dl_oldest, folder_to_all_items)
			(dl_every, dl_number, dl_oldest, dl_quit) = menu_data
			if dl_quit: 
				break
		except KeyboardInterrupt as e:
			console.control_c()

main()