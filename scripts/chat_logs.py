#!/usr/bin/python

import pyautogui
import pyperclip
import difflib

import os
from os.path import expanduser

from datetime import datetime
from time import sleep

import pygtk
pygtk.require('2.0')
import gtk
import wnck
import re
import sys
import time

import subprocess

home = expanduser("~")
chat_home_dir = "{}/git/john/minas/chat_logs".format(home)

MIN_IDLE = 5000
MAX_TRIES = 10

rooms = [
'thinkScript Lounge',
'Trader Lounge'
]

# commit chat logs
def commit_chat_logs():
	NO_CHANGES = 'nothing to commit, working tree clean'
	status = subprocess.check_output(
		['git status'],
		cwd="{}/git/john/minas/chat_logs".format(home),
		shell=True
		)
	print(status)

	if NO_CHANGES in status:
		print("No changes to commit.")
	else:

		# git commit
		add = subprocess.check_output(
			['git add .'],
			cwd=chat_home_dir,
			shell=True
			)
		print(add)

		commit = subprocess.check_output(
			['git commit -m "autocommit chat logs"'],
			cwd=chat_home_dir,
			shell=True
			)
		print(commit)

		commit = subprocess.check_output(
			['for i in `git remote `; do git push $i master; done'],
			cwd=chat_home_dir,
			shell=True
			)
		print(commit)


def get_chat_logs_on_idle():

	for tries in xrange(0, MAX_TRIES):
		if tries >= MAX_TRIES:
			print("Too busy to run.")
			sys.exit(1)

		idle = subprocess.check_output(['xprintidle'])
		idle = int(idle)
		if idle > MIN_IDLE:
			break
		else:
			print("Idle at {}. Waiting for greater than {}".format(
				idle, MIN_IDLE))
		sleep(3)

	#TODO: get current active window and focus back after copying text

	active_window = None
	room_windows = {}

	screen = wnck.screen_get_default()
	while gtk.events_pending():
		gtk.main_iteration()
		
		windows = screen.get_windows()
		active_window = screen.get_active_window()
		for w in windows:
			for room in rooms:
				titlePattern = re.compile('.*{}.*'.format(room))
				if titlePattern.match(w.get_name()):
					room_windows[room] = w

	print(room_windows)

	for room, w in room_windows.iteritems():
		print(w.get_name())
		print(w.get_pid())
		w.activate(0)
		x, y, width, height = w.get_client_window_geometry()

		pyautogui.click(x=x+20, y=y+height/2)
		sleep(.2)
		pyautogui.hotkey('ctrl', 'a')
		sleep(.5)
		pyautogui.hotkey('ctrl', 'c')
		sleep(.5)
		data = pyperclip.paste()
		# print("data: {}".format(data))

		filename = "{r}-{d}.txt".format(
			r=room.replace(' ', ''),
			d=datetime.now().strftime("%Y%m%d")
			)

		folder = '{c}/{r}'.format(c=chat_home_dir, r=room)
		if not os.path.exists(folder):
		    os.mkdir(folder)

		old_data = ''
		try:
			chat_log = '{dir}/{f}'.format(
				dir=folder,
				f=filename)
			with open(chat_log, 'r') as f:
				old_data = f.read()
		except IOError:
			pass

		if old_data:
			diff = difflib.ndiff(old_data.split('\n'), data.split('\n'))
			changes = [l[2:] for l in diff if l.startswith('+ ') or l.startswith('- ')]
			changes = [x for x in changes if x != '']
			print("{} new lines".format(len(changes)))
			if len(changes) > 0:
				data = '\n'.join(changes)
			else:
				continue
		else:
			print("Writing new file.")

		mode = 'a' if os.path.exists(chat_log) else 'w'
		with open(chat_log, mode) as f:
			f.write(data)

		# deduplicate to make sure difflib didnt mess up 
		cmd = "awk '!seen[$0]++ == 1' '{f}' > '{f}.tmp' && mv '{f}.tmp' '{f}' ".format(f=chat_log)
		print(cmd)
		out = subprocess.check_output(
	           [cmd],
				cwd=chat_home_dir,
				shell=True
				)
		print(out)
		sleep(1)

	active_window.activate(0)


def main():
	get_chat_logs_on_idle()
	commit_chat_logs()


if __name__ == '__main__':
	main()