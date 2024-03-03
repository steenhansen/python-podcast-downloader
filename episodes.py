
from pathlib import Path

from urllib.request import urlopen

from time import sleep

import os
import requests
import json
import xmltodict
import podcasts
import re
import console

POD_CHUNK_SIZE = 256 * 256 #65536
MAX_FN_CHARS = 240
APPEND_BINARY_EPI = 'ab'
VALID_FILE_NAME = re.compile(r"[^a-z A-Z0-9\\.\\-]")

def valid_url(epi_url):
	with requests.get(epi_url, stream=True) as epi_req:
		if epi_req.status_code==200:
			return ""
		elif epi_req.status_code==403:
			return str(403) + " Forbidden"
		else:
			return epi_req.status_code

def bad_url(url_error, epi_url):
	print("         Error bad episode -", url_error, '-', epi_url)

def delete_file(write_path):
	bad_file = Path(write_path)
	if bad_file.is_file():
		Path.unlink(bad_file)

def stream_url(epi_url, write_path):
	file_done = False
	url_error = valid_url(epi_url)
	if url_error:
		bad_url(url_error, epi_url)
	else:
		with open(write_path, APPEND_BINARY_EPI) as epi_file:
			time_out = False
			with requests.get(epi_url, stream=True) as epi_req:
				if epi_req.status_code==200:
					chunked_bytes =0
					for epi_chunk in epi_req.iter_content(chunk_size=POD_CHUNK_SIZE):
						epi_file.write(epi_chunk)
						chunked_bytes = console.current_bytes(chunked_bytes, write_path, len(epi_chunk))
					print("")
					file_done = True
				else:
					time_out = True
					bad_url(epi_req.status_code, epi_url)
		if time_out:
			delete_file(write_path)
	return file_done

# fails for 'http://feeds.soundcloud.com/users/soundcloud:users:572119410/sounds.rss'
def BAD_get_rss_file(pod_url):
	rss_str = ""
	with requests.get(pod_url) as pod_req:
		for pod_line in pod_req.iter_lines():
			str_line = pod_line.decode()
			rss_str = rss_str + str_line
	return rss_str

def get_rss_file(pod_url):
	html = urlopen(pod_url)
	html_bytes = html.read()
	rss_str = html_bytes.decode("utf-8")
	return rss_str

def get_channel(rss_str):
	try:
		json_rss = xmltodict.parse(rss_str)
		epi_items = json_rss['rss']
		channel_items = epi_items['channel']['item']
	except Exception as e:
		print("\n\nConnection issue - ", str(e), "\n")
		channel_items = []
	return channel_items

def download_files(pod_dir, missing_episodes):
	for an_epi in missing_episodes:
		write_file, epi_url = an_epi
		run_dir = os.getcwd()
		numbered_fname = os.path.join(run_dir, pod_dir, write_file)
		stream_url(epi_url, numbered_fname)
		sleep(1)

def update_folder(fold_name, dl_every, dl_number, dl_oldest, all_episodes):
	new_episodes = already_have(fold_name, all_episodes)
	if dl_every:
		download_files(fold_name, new_episodes)
	else:
		if dl_oldest:
			new_episodes.reverse()
		short_episode_list = []
		for an_item in new_episodes:
			short_episode_list.append(an_item)
			dl_number -= 1
			if dl_number ==0:
				break
		download_files(fold_name, short_episode_list)


	# we need to winnow away bad enclosures so they don't appear in the count
	# https://www.wnycstudios.org/feeds/series/podcasts?limit=123456
def good_enclosures(channel_items):
	good_enclosures =0
	for an_item in channel_items:
		if 'enclosure' in an_item:
			good_enclosures +=1
	return good_enclosures

def get_items(fold_name):
	run_dir = os.getcwd()
	rss_name = os.path.join(run_dir, fold_name, podcasts.RSS_FILE_NAME)
	with open(rss_name, "r") as rss_file:
		rss_url = rss_file.readline()
	rss_str = get_rss_file(rss_url)
	channel_items = get_channel(rss_str)
	item_count =  good_enclosures(channel_items)
	all_episodes = []
	for an_item in channel_items:
		epi_data = item_data(an_item, item_count)
		if epi_data != None:
			all_episodes.append(epi_data)
			item_count -=1
	return all_episodes

def item_data(an_item, item_count):
	try:
		epi_type = an_item['enclosure']['@type']
		epi_title = indexed_fname(item_count, an_item['title'], epi_type)
		epi_url = an_item['enclosure']['@url']
		epi_data = (epi_title, epi_url)
		return epi_data
	except Exception as e:
		return None

def already_have(fold_name, all_episodes):
	run_dir = os.getcwd()
	episodes_new = []
	for an_epi in all_episodes:
		(file_name, _epi_url) = an_epi
		write_file = os.path.join(run_dir, fold_name, file_name)
		my_file = Path(write_file)
		if not my_file.is_file():
			episodes_new.append(an_epi)
	return episodes_new



def indexed_fname(epi_count, epi_title, epi_type):
	four_digits = f"{epi_count:04d}-"
	valid_fname_long = VALID_FILE_NAME.sub("", epi_title)
	valid_fname_short = valid_fname_long[:MAX_FN_CHARS]
	match epi_type:
		case "image/jpeg":
			extension = ".jpg"
		case "image/png":
			extension = ".png"
		case "application/pdf":
			extension = ".pdf"
		case "audio/mpeg":
			extension = ".mp3"
		case _:
			extension = ".unk"
	numbered_fname = four_digits + valid_fname_short + extension
	return numbered_fname
