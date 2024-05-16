
from sys import stdout

import sys
import os

BACKSPACE_TO_START = "\r\x1b[K"
MAX_SCREN_CHARS = 100
CONTROL_C_SIGNAL = 130

def current_bytes(byte_count, file_name, chunk_len):
	file_name = file_name[:MAX_SCREN_CHARS]
	stdout.write(BACKSPACE_TO_START + byte_count.__str__())
	stdout.write(" - " + file_name)
	stdout.flush()
	byte_count = byte_count + chunk_len
	return byte_count

def read_folder(dir_stat):
	stdout.write(BACKSPACE_TO_START + dir_stat)
	stdout.flush()

def control_c():
	print('bye')
	try:
		sys.exit(CONTROL_C_SIGNAL)
	except SystemExit:
		os._exit(CONTROL_C_SIGNAL)