
from urllib import parse
from pathlib import Path

import re
import unicodedata
import episodes

DEF_HTTP_SCHEME="http://"
DOMAIN_DOT_DOMAIN = re.compile("[a-zA-Z0-9]+\\.[a-zA-Z0-9]+")
RSS_FILE_NAME="rss_url.txt"

def django_slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.

    https://stackoverflow.com/questions/295135/turn-a-string-into-a-valid-filename
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')

def input_fold_name():
	fold_name = input('Podcast folder name: ')
	slugged_name = django_slugify(fold_name)
	fold_path = (Path.cwd() / slugged_name)
	folder_exists = Path(fold_path).is_dir()
	if folder_exists :
		print(fold_path, "exists, try again: ")
		return input_fold_name()
	return fold_path

def input_url():
	pod_url = input('Podcast RSS feed url: ')
	parsed_url = parse.urlparse(pod_url)
	if parsed_url.netloc=='':
		with_scheme = DEF_HTTP_SCHEME + parsed_url.geturl()
		parsed_url = parse.urlparse(with_scheme)  # a.com/podcasts
		has_domains = DOMAIN_DOT_DOMAIN.search(parsed_url.netloc)
		if not has_domains:
			print("Bad url, try again, a.com: ")    # /podcasts  
			return input_url()                           
	pod_url = parsed_url.geturl()   # https://a.com/podcasts
	return pod_url

def check_url(pod_url):
	try:
		rss_file = episodes.get_rss_file(pod_url)
		last_episode = episodes.all_items(rss_file, 0, False)
		if len(last_episode)>0:
			return True
		else:
			return False
	except Exception as e:
		#print("check_url EX", str(e))
		return False

def valid_rss():
	is_rss = False
	while not is_rss: 
		pod_url = input_url()
		is_rss = check_url(pod_url)
	return pod_url

def make_folder(fold_path, pod_url):
	fold_path = Path(fold_path)
	fold_path.mkdir()
	rss_name = fold_path / RSS_FILE_NAME
	with rss_name.open("w", encoding ="utf-8") as rss_file:
		rss_file.write(pod_url)

def add_folder():
	fold_path = input_fold_name()
	pod_url = valid_rss()
	make_folder(fold_path, pod_url)
